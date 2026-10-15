"""Tests for entities created when their data first appears (issue #74).

On the SCD923 the SenseIQ data points arrive only as LAN pushes, after the first
cloud poll, so platforms must be able to add an entity group later than setup.
"""

from entity import add_entities_when_ready, dps_present


class FakeCoordinator:
    """The two things the helper uses: `data` and `async_add_listener`."""

    def __init__(self, data=None):
        self.data = data
        self.listeners = []

    def async_add_listener(self, callback):
        self.listeners.append(callback)
        return lambda: self.listeners.remove(callback)

    def push(self, dps):
        """What a LAN push does: merge the DPS and notify the listeners."""
        self.data = {**(self.data or {}), **dps}
        for callback in list(self.listeners):
            callback()


def setup(coordinator, groups):
    added, unloads = [], []
    add_entities_when_ready(coordinator, added.extend, groups, unloads.append)
    return added, unloads


class TestAtStartup:
    def test_group_with_its_data_is_added_immediately(self):
        coordinator = FakeCoordinator({"3": '{"r":"o","br":0}'})
        added, _ = setup(coordinator, [(dps_present("3"), lambda: ["breathing"])])
        assert added == ["breathing"]

    def test_no_listener_when_nothing_is_pending(self):
        coordinator = FakeCoordinator({"3": "x"})
        _, unloads = setup(coordinator, [(dps_present("3"), lambda: ["breathing"])])
        assert coordinator.listeners == []
        assert unloads == []

    def test_missing_data_adds_nothing_yet(self):
        coordinator = FakeCoordinator({"207": 2345})
        added, _ = setup(coordinator, [(dps_present("3"), lambda: ["breathing"])])
        assert added == []

    def test_no_data_at_all_does_not_raise(self):
        coordinator = FakeCoordinator(None)
        added, _ = setup(coordinator, [(dps_present("3"), lambda: ["breathing"])])
        assert added == []


class TestLaterPush:
    def test_group_is_added_when_its_data_first_arrives(self):
        coordinator = FakeCoordinator({"207": 2345})
        added, _ = setup(coordinator, [(dps_present("3"), lambda: ["breathing"])])
        coordinator.push({"3": '{"r":"b","br":35}'})
        assert added == ["breathing"]

    def test_group_is_added_only_once(self):
        coordinator = FakeCoordinator({})
        added, _ = setup(coordinator, [(dps_present("3"), lambda: ["breathing"])])
        coordinator.push({"3": "a"})
        coordinator.push({"3": "b"})
        coordinator.push({"207": 2100})
        assert added == ["breathing"]

    def test_groups_are_independent(self):
        coordinator = FakeCoordinator({"12": True})
        added, _ = setup(coordinator, [
            (dps_present("12"), lambda: ["cry_alert"]),
            (dps_present("3"), lambda: ["breathing"]),
        ])
        assert added == ["cry_alert"]
        coordinator.push({"3": "x"})
        assert added == ["cry_alert", "breathing"]

    def test_unrelated_updates_add_nothing(self):
        coordinator = FakeCoordinator({})
        added, _ = setup(coordinator, [(dps_present("3"), lambda: ["breathing"])])
        coordinator.push({"207": 2345, "246": "playing"})
        assert added == []

    def test_readiness_can_inspect_the_value(self):
        # The breathing group waits for a decodable status, not just the key.
        coordinator = FakeCoordinator({"3": ""})
        added, _ = setup(coordinator, [(lambda dps: bool(dps.get("3")), lambda: ["breathing"])])
        assert added == []
        coordinator.push({"3": '{"r":"b","br":35}'})
        assert added == ["breathing"]


class TestUnload:
    def test_listener_is_handed_to_unload(self):
        coordinator = FakeCoordinator({})
        _, unloads = setup(coordinator, [(dps_present("3"), lambda: ["breathing"])])
        assert len(coordinator.listeners) == 1
        unloads[0]()
        assert coordinator.listeners == []


class TestFailingGroup:
    def test_a_group_that_fails_to_build_does_not_block_the_others(self):
        def boom():
            raise ValueError("bad payload")

        coordinator = FakeCoordinator({})
        added, _ = setup(coordinator, [
            (dps_present("3"), boom),
            (dps_present("3"), lambda: ["breathing"]),
        ])
        coordinator.push({"3": "x"})
        assert added == ["breathing"]

    def test_a_failed_group_is_not_retried_on_every_push(self):
        calls = []

        def boom():
            calls.append(1)
            raise ValueError("bad payload")

        coordinator = FakeCoordinator({})
        setup(coordinator, [(dps_present("3"), boom)])
        coordinator.push({"3": "x"})
        coordinator.push({"3": "y"})
        assert calls == [1]

