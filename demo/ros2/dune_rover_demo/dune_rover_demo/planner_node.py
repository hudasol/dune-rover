"""ROS 2 node around the shipped Dune Rover Planner (dunerover.planner). SIMULATED BY ME; not field software.

    dune_rover_planner  reads an elevation model (parameter `dem`, a GeoTIFF; a synthetic dune field when empty),
                        assesses it with the product (`posting`, `vehicle`, `draws`), and
                        publishes  /dune_rover/map               nav_msgs/OccupancyGrid  free 0 = TRAVERSABLE, occupied 100 =
                                                                  BLOCKED or NO DATA, unknown -1 = every UNKNOWN class
                                   /dune_rover/face_probability  nav_msgs/OccupancyGrid  face probability times 100
                                   /dune_rover/info              std_msgs/String         JSON: resolution gate, vehicle,
                                                                  climbing limits, grid corner in the input's map units
                        (all latched: transient local durability), and serves
                                   /dune_rover/plan              nav_msgs/srv/GetPlan    start and goal poses in the map frame
                                                                  -> nav_msgs/Path through cell centres; the warnings of the
                                                                  route are published on /dune_rover/plan_warnings (String).
The map frame is a local metre frame with its origin at the lower left corner of the grid (x east, y north), as in the
Nav2 export of the planner. Parameter `policy` chooses naive, conservative or risk_weighted (default conservative).

Smoke test (one request on the synthetic dune field, result in results/ros2_planner/smoke_test.json):

    micromamba run -p /opt/mm/ros2 python demo/ros2/dune_rover_demo/dune_rover_demo/planner_node.py --smoke-test
"""
from __future__ import annotations
import json, os, sys, time
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

import rclpy  # noqa: E402
from rclpy.node import Node  # noqa: E402
from rclpy.qos import QoSProfile, DurabilityPolicy  # noqa: E402
from std_msgs.msg import String  # noqa: E402
from nav_msgs.msg import OccupancyGrid, Path  # noqa: E402
from nav_msgs.srv import GetPlan  # noqa: E402
from geometry_msgs.msg import PoseStamped  # noqa: E402

from dunerover import planner as P  # noqa: E402
from dunerover.cli import synthetic_dunes, climbing_limits_line  # noqa: E402


def occupancy_values(classes: np.ndarray) -> np.ndarray:
    """ROS occupancy values (row 0 = south, as OccupancyGrid expects): 0 free, 100 occupied, -1 unknown."""
    occ = np.full(classes.shape, -1, dtype=np.int8)
    occ[classes == 0] = 0
    occ[np.isin(classes, (1, 5))] = 100
    return np.flipud(occ)


class PlannerNode(Node):
    def __init__(self, **kwargs):
        super().__init__("dune_rover_planner", **kwargs)
        for name, default in (("dem", ""), ("posting", 0.0), ("vehicle", "assumed"), ("draws", 128), ("policy", "conservative"),
                              ("frame_id", "map")):
            self.declare_parameter(name, default)
        g = lambda n: self.get_parameter(n).value
        dem = g("dem")
        r = P.read_raster(dem) if dem else P.raster_from_array(synthetic_dunes(), 2.0, "SYNTHETIC dune field")
        posting = float(g("posting")) or None
        if dem == "" and posting is None:
            posting = 10.0
        prof = P.builtin_profile(g("vehicle")) if g("vehicle") in P.BUILTIN_PROFILES else P.VehicleProfile.load(g("vehicle"))
        self.a = P.assess(r, posting, prof, n_draws=int(g("draws")))
        self.policy = g("policy")
        self.frame = g("frame_id")
        self.nr, self.nc = self.a.classes.shape
        self.dx, self.dy = self.a.dem.dx, self.a.dem.dy
        latched = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.pub_map = self.create_publisher(OccupancyGrid, "/dune_rover/map", latched)
        self.pub_face = self.create_publisher(OccupancyGrid, "/dune_rover/face_probability", latched)
        self.pub_info = self.create_publisher(String, "/dune_rover/info", latched)
        self.pub_warn = self.create_publisher(String, "/dune_rover/plan_warnings", 10)
        self.srv = self.create_service(GetPlan, "/dune_rover/plan", self.on_plan)
        self.pub_map.publish(self.grid(occupancy_values(self.a.classes)))
        self.pub_face.publish(self.grid(np.flipud(np.round(100 * self.a.face_prob)).astype(np.int8)))
        x, y = self.a.raster.map_xy(self.nr - 0.5, -0.5)
        info = {"label": "SIMULATED BY ME", "gate": self.a.gate["status"], "message": self.a.gate["message"],
                "posting_m": self.a.posting_m, "policy": self.policy, "vehicle": prof.name, "limits": climbing_limits_line(prof),
                "lower_left_corner_map_units": [float(x), float(y)], "epsg": self.a.raster.epsg, "geographic": self.a.raster.geographic}
        self.pub_info.publish(String(data=json.dumps(info)))
        self.get_logger().info(f"map {self.nr} x {self.nc} at {self.a.posting_m:g} m, gate {self.a.gate['status']}")

    def grid(self, values: np.ndarray) -> OccupancyGrid:
        m = OccupancyGrid()
        m.header.frame_id = self.frame
        m.header.stamp = self.get_clock().now().to_msg()
        m.info.resolution = float(np.sqrt(self.dx * self.dy))
        m.info.width, m.info.height = int(self.nc), int(self.nr)
        m.info.origin.orientation.w = 1.0
        m.data = values.astype(np.int8).ravel().tolist()
        return m

    def to_cell(self, pose: PoseStamped):
        c = int(np.floor(pose.pose.position.x / self.dx)); r = self.nr - 1 - int(np.floor(pose.pose.position.y / self.dy))
        return r, c

    def on_plan(self, req, resp):
        path = Path(); path.header.frame_id = self.frame; path.header.stamp = self.get_clock().now().to_msg()
        try:
            rp = P.plan(self.a, self.to_cell(req.start), self.to_cell(req.goal), self.policy)
        except ValueError as exc:
            self.pub_warn.publish(String(data=json.dumps({"reachable": False, "reason": str(exc)})))
            resp.plan = path
            return resp
        if rp.reachable:
            for r, c in rp.rc:
                ps = PoseStamped(); ps.header = path.header
                ps.pose.position.x = float((c + 0.5) * self.dx); ps.pose.position.y = float((self.nr - r - 0.5) * self.dy)
                ps.pose.orientation.w = 1.0
                path.poses.append(ps)
        self.pub_warn.publish(String(data=json.dumps({"reachable": rp.reachable, "policy": rp.policy, "metrics": rp.metrics,
                                                      "warnings": rp.warnings}, default=float)))
        resp.plan = path
        return resp


def smoke_test():
    """One request with the naive policy (on the synthetic field every east west route crosses 32 degree lee faces, which the
    cautious policies refuse to descend), then the same request with the conservative policy, which must refuse it."""
    from rclpy.parameter import Parameter
    rclpy.init()
    node = PlannerNode(parameter_overrides=[Parameter("policy", value="naive")])
    client = rclpy.create_node("dune_rover_planner_client")
    got = {}
    sub_map = client.create_subscription(OccupancyGrid, "/dune_rover/map", lambda m: got.setdefault("map", m),
                                         QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL))
    sub_w = client.create_subscription(String, "/dune_rover/plan_warnings", lambda m: got.setdefault("warn", json.loads(m.data)), 10)
    cli = client.create_client(GetPlan, "/dune_rover/plan")
    ex = rclpy.executors.SingleThreadedExecutor(); ex.add_node(node); ex.add_node(client)
    t0 = time.time()
    while not cli.wait_for_service(timeout_sec=0.1) and time.time() - t0 < 10:
        ex.spin_once(timeout_sec=0.1)
    req = GetPlan.Request()
    req.start.pose.position.x, req.start.pose.position.y = 25.0, 0.5 * node.nr * node.dy
    req.goal.pose.position.x, req.goal.pose.position.y = node.nc * node.dx - 25.0, 0.5 * node.nr * node.dy
    fut = cli.call_async(req)
    while (not fut.done() or "warn" not in got or "map" not in got) and time.time() - t0 < 60:
        ex.spin_once(timeout_sec=0.1)
    path = fut.result().plan
    m = got["map"]
    node.policy = "conservative"; got.pop("warn", None)
    fut2 = cli.call_async(req)
    while (not fut2.done() or "warn" not in got) and time.time() - t0 < 90:
        ex.spin_once(timeout_sec=0.1)
    refused = got.get("warn")
    out = {"label": "SIMULATED BY ME (synthetic dune field); ROS 2 smoke test of the shipped planner behind a service",
           "ros_distro": os.environ.get("ROS_DISTRO", ""), "map_width": m.info.width, "map_height": m.info.height,
           "map_resolution_m": m.info.resolution, "occupancy_counts": {str(v): int(np.sum(np.array(m.data) == v)) for v in (-1, 0, 100)},
           "naive_path_poses": len(path.poses), "conservative_reply": refused, "seconds": round(time.time() - t0, 2),
           "date": time.strftime("%Y-%m-%d %H:%M:%S")}
    os.makedirs(os.path.join(ROOT, "results", "ros2_planner"), exist_ok=True)
    with open(os.path.join(ROOT, "results", "ros2_planner", "smoke_test.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k != "conservative_reply"}))
    node.destroy_node(); client.destroy_node(); rclpy.shutdown()
    return out


def main():
    rclpy.init()
    node = PlannerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node(); rclpy.shutdown()


if __name__ == "__main__":
    if "--smoke-test" in sys.argv:
        smoke_test()
    else:
        main()
