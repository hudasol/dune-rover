"""ROS 2 nodes of the closed loop demonstration (stage 23). SIMULATED BY ME on PUBLISHED USGS 3DEP lidar; not field software.

Three nodes talk only through ROS 2 topics:
  map_planner   publishes the 30 m three class map (/dune_map, nav_msgs/OccupancyGrid: TRAVERSABLE 0, UNKNOWN 50,
                BLOCKED 100) and a route (/plan, nav_msgs/Path) from the rover's latest pose to the goal; on
                /blocked_cells (std_msgs/Int32MultiArray) it removes those cells from its graph and replans.
  rover_sim     drives the latest /plan over the one metre lidar surface with the slip model of demo/closed_loop.py,
                and publishes /odom (nav_msgs/Odometry, position with 0.3 m noise per axis), /wheel_distance
                (std_msgs/Float64, cumulative odometry) and /rover_status (std_msgs/String).
  slip_monitor  estimates slip from /odom and /wheel_distance over the last 10 m (/slip_estimate, std_msgs/Float64)
                and, when the estimate reaches 0.5, publishes the cells of the next 15 m of /plan on /blocked_cells.
The physics, the map, the planner and the thresholds are those of demo/closed_loop.py; this package only puts them
behind topics. Run the smoke test (one origin destination pair) with:

    micromamba run -p /opt/mm/ros2 python demo/ros2/dune_rover_demo/dune_rover_demo/nodes.py --site WhiteSands --pair 0
"""
from __future__ import annotations
import argparse, json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "scripts")); sys.path.insert(0, os.path.join(ROOT, "demo"))

import rclpy  # noqa: E402
from rclpy.node import Node  # noqa: E402
from rclpy.executors import SingleThreadedExecutor  # noqa: E402
from std_msgs.msg import Float64, String, Int32MultiArray  # noqa: E402
from nav_msgs.msg import OccupancyGrid, Path, Odometry  # noqa: E402
from geometry_msgs.msg import PoseStamped  # noqa: E402

import closed_loop as CL  # noqa: E402
import planner_lidar as PL  # noqa: E402
import terrain_validation_lidar as TV  # noqa: E402

K = 30   # map posting, m


class World:
    """Map, graph and one origin destination pair, built once and shared by the nodes (as a map server would)."""

    def __init__(self, site, pair):
        from dunerover.terrain import horn_gradient
        from dunerover.slipmodel import apply_range_set, nominal_params
        from dunerover import subgrid as SG, threeclass as TC
        apply_range_set("original")
        fname, win, _ = TV.SITES[site]
        z1, _ = TV.load_window(fname, win)
        self.z1 = np.where(np.isnan(z1), np.nanmean(z1), z1)
        draws = TC.lhs_draws(256, TV.SEED)
        self.dem, eg, self.cls, pf = PL.build_map(self.z1, K, draws, SG.fit(float(K), "base", 1.0))
        self.g = PL.policy_graph(eg, self.cls, pf, "naive", nominal_params())
        sl30 = np.degrees(np.arctan(np.hypot(*horn_gradient(self.dem.z, 30.0, 30.0))))
        cand = np.argwhere((self.cls == 0) & (sl30 < 5.0))
        cand = cand[(cand[:, 0] > 2) & (cand[:, 0] < self.cls.shape[0] - 3) & (cand[:, 1] > 2) & (cand[:, 1] < self.cls.shape[1] - 3)]
        rng = np.random.default_rng(PL.SEED_OD); pairs = []; tries = 0
        while len(pairs) < PL.N_PAIRS and tries < 50000:
            tries += 1
            a, b = cand[rng.integers(len(cand))], cand[rng.integers(len(cand))]
            if np.hypot(*(a - b)) * 30 >= PL.MIN_SEP:
                pairs.append((a, b))
        a, b = pairs[pair]
        self.start, self.goal = (int(a[0]), int(a[1])), (int(b[0]), int(b[1]))
        self.nc = self.dem.shape[1]
        self.seed = CL.SEED + pair


def cell_to_xy(rc):
    return float((rc[1] + 0.5) * K), float((rc[0] + 0.5) * K)   # x = column metres, y = row metres (map frame)


class MapPlanner(Node):
    def __init__(self, w: World):
        super().__init__("map_planner")
        self.w, self.g, self.cur, self.replans = w, w.g.copy(), w.start, 0
        self.pub_map = self.create_publisher(OccupancyGrid, "/dune_map", 1)
        self.pub_plan = self.create_publisher(Path, "/plan", 1)
        self.create_subscription(Odometry, "/odom", self.on_odom, 10)
        self.create_subscription(Int32MultiArray, "/blocked_cells", self.on_blocked, 10)
        self.create_timer(0.2, self.publish_map_once)
        self.map_sent = False
        self.create_timer(0.3, self.first_plan)
        self.planned = False

    def publish_map_once(self):
        if self.map_sent:
            return
        m = OccupancyGrid(); m.header.frame_id = "map"; m.info.resolution = float(K)
        m.info.width, m.info.height = int(self.w.cls.shape[1]), int(self.w.cls.shape[0])
        occ = np.where(self.w.cls == 0, 0, np.where(self.w.cls == 1, 100, 50)).astype(np.int8)
        m.data = occ.ravel().tolist(); self.pub_map.publish(m); self.map_sent = True

    def first_plan(self):
        if not self.planned:
            self.planned = True; self.plan()

    def plan(self):
        rc = PL.route(self.g, self.w.nc, self.cur, self.w.goal)
        p = Path(); p.header.frame_id = "map"
        if rc is not None:
            for r in rc:
                ps = PoseStamped(); ps.header.frame_id = "map"; ps.pose.position.x, ps.pose.position.y = cell_to_xy(r); p.poses.append(ps)
        self.pub_plan.publish(p)
        self.get_logger().info(f"plan from {self.cur}: {len(p.poses)} cells (replans {self.replans})")

    def on_odom(self, msg):
        self.cur = (int(msg.pose.pose.position.y // K), int(msg.pose.pose.position.x // K))

    def on_blocked(self, msg):
        if self.replans >= CL.MAX_REPLANS:
            return
        self.replans += 1
        g = self.g.tolil()
        for b in msg.data:
            if b != self.cur[0] * self.w.nc + self.cur[1]:
                g[:, int(b)] = 0
        self.g = g.tocsr(); self.g.eliminate_zeros()
        self.plan()


class RoverSim(Node):
    def __init__(self, w: World):
        super().__init__("rover_sim")
        self.w, self.rng = w, np.random.default_rng(w.seed)
        self.sp, self.s_true, self.i, self.odo, self.run, self.status = None, None, 0, 0.0, 0, "waiting"
        self.pub_odom = self.create_publisher(Odometry, "/odom", 10)
        self.pub_wd = self.create_publisher(Float64, "/wheel_distance", 10)
        self.pub_status = self.create_publisher(String, "/rover_status", 10)
        self.create_subscription(Path, "/plan", self.on_plan, 10)
        self.create_timer(0.002, self.step)
        self.metres = 0

    def on_plan(self, msg):
        if self.status in ("entrapped", "arrived"):
            return
        if not msg.poses:
            self.status = "stopped (no route)"; self.pub_status.publish(String(data=self.status)); return
        rc = np.array([[p.pose.position.y // K, p.pose.position.x // K] for p in msg.poses], dtype=float)
        self.sp, _ = CL.resample(rc, K)
        self.s_true = CL.true_slip_along(self.sp, self.w.z1, self.rng)
        self.i, self.status = 0, "driving"

    def step(self):
        if self.status != "driving":
            return
        if self.i >= len(self.sp) - 1:
            self.status = "arrived"; self.pub_status.publish(String(data=self.status)); return
        st = self.s_true[self.i]
        self.run = self.run + 1 if st >= CL.STUCK_SLIP else 0
        if self.run >= CL.STUCK_RUN:
            self.status = "entrapped"; self.pub_status.publish(String(data=self.status)); return
        self.odo += 1.0 / max(1.0 - st, 1e-3); self.i += 1; self.metres += 1
        y, x = self.sp[self.i]                  # one metre posts: row is y, column is x
        o = Odometry(); o.header.frame_id = "map"
        o.pose.pose.position.x = float(x + self.rng.normal(0, CL.GNSS_SD)); o.pose.pose.position.y = float(y + self.rng.normal(0, CL.GNSS_SD))
        self.pub_wd.publish(Float64(data=self.odo)); self.pub_odom.publish(o)


class SlipMonitor(Node):
    def __init__(self):
        super().__init__("slip_monitor")
        self.fix, self.odo, self.plan_xy, self.latest = [], [], None, float("nan")
        self.pub_est = self.create_publisher(Float64, "/slip_estimate", 10)
        self.pub_block = self.create_publisher(Int32MultiArray, "/blocked_cells", 10)
        self.create_subscription(Float64, "/wheel_distance", self.on_wd, 10)
        self.create_subscription(Odometry, "/odom", self.on_odom, 10)
        self.create_subscription(Path, "/plan", self.on_plan, 10)
        self.nc = None
        self.estimates = []

    def on_plan(self, msg):
        self.plan_xy = np.array([[p.pose.position.x, p.pose.position.y] for p in msg.poses]) if msg.poses else None
        self.fix, self.odo = [], []

    def on_wd(self, msg):
        self.odo.append(msg.data)

    def on_odom(self, msg):
        self.fix.append((msg.pose.pose.position.x, msg.pose.pose.position.y))
        n = min(len(self.fix), len(self.odo))
        if n <= CL.WINDOW:
            return
        d = float(np.hypot(self.fix[n - 1][0] - self.fix[n - 1 - CL.WINDOW][0], self.fix[n - 1][1] - self.fix[n - 1 - CL.WINDOW][1]))
        o = self.odo[n - 1] - self.odo[n - 1 - CL.WINDOW]
        s_hat = 1.0 - d / o
        self.pub_est.publish(Float64(data=s_hat)); self.estimates.append(s_hat)
        if s_hat >= CL.TRIGGER and self.plan_xy is not None and self.nc:
            p = np.array(self.fix[n - 1])
            j = int(np.argmin(np.hypot(*(self.plan_xy - p).T)))
            ahead = self.plan_xy[j + 1:j + 1 + int(np.ceil(CL.LOOKAHEAD / K)) + 1]
            cells = [int((y // K) * self.nc + (x // K)) for x, y in ahead]
            self.pub_block.publish(Int32MultiArray(data=cells)); self.plan_xy = None
            self.get_logger().info(f"slip estimate {s_hat:.2f}: blocking {len(cells)} cells ahead")


def smoke_test(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--site", default="WhiteSands"); ap.add_argument("--pair", type=int, default=0)
    ap.add_argument("--timeout", type=float, default=240.0); ap.add_argument("--out", default=os.path.join(ROOT, "results", "closed_loop", "ros2_smoke_test.json"))
    a = ap.parse_args(argv)
    w = World(a.site, a.pair)
    rclpy.init()
    mp, rv, sm = MapPlanner(w), RoverSim(w), SlipMonitor()
    sm.nc = w.nc
    ex = SingleThreadedExecutor()
    for n in (mp, rv, sm):
        ex.add_node(n)
    t0 = time.time()
    while time.time() - t0 < a.timeout and rv.status not in ("arrived", "entrapped", "stopped (no route)"):
        ex.spin_once(timeout_sec=0.01)
    res = {"label": "SIMULATED BY ME: ROS 2 smoke test of the closed loop demonstration (one origin destination pair)", "site": a.site, "pair": a.pair,
           "outcome": rv.status, "metres_driven": rv.metres, "replans": mp.replans, "slip_estimates_published": len(sm.estimates),
           "max_slip_estimate": round(max(sm.estimates), 3) if sm.estimates else None, "wall_s": round(time.time() - t0, 1),
           "ros_distro": os.environ.get("ROS_DISTRO", "jazzy (RoboStack)")}
    print(json.dumps(res))
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(res, open(a.out, "w"), indent=1)
    for n in (mp, rv, sm):
        n.destroy_node()
    rclpy.shutdown()
    return res


if __name__ == "__main__":
    smoke_test()
