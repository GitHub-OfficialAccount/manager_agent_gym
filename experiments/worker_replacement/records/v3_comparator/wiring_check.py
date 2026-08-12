"""Confirm the 12 real fallback judgments route through the INTEGRATED path.

The probe measured the detector; this measures the wiring. Probe/production
input divergence is the defect class that has bitten this investigation three
times, so the counters are read from a real extractor run over the real packets.
"""
import asyncio, collections, glob, json, sys
from pathlib import Path
sys.path.insert(0, "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym")
from experiments.worker_replacement.arm3_relations import (
    Arm3SemanticExtractor, RelationPacket, judgments_for,
)

ROOT = "/home/therealgod/Projects/AdHocTeamwork/manager_agent_gym"

async def main():
    packets = []
    for path in sorted(glob.glob(f"{ROOT}/experiments/worker_replacement/outputs/smoke101_5b19b5b/*arm3*/arm3_state.json")):
        for entry in json.loads(Path(path).read_text())["extraction"]["packet_audit"]:
            packet = RelationPacket.model_validate(entry["packet"])
            js = judgments_for(packet)
            if js and js[0].payload.get("method_extraction") == "full_text_fallback":
                packets.append(packet)
    # JOIN ASSERTION: an empty set here looks identical to a clean result.
    assert packets, "no fallback packets found -- join failed, not a clean result"
    print(f"fallback packets found: {len(packets)}", flush=True)

    extractor = Arm3SemanticExtractor(model="openrouter/deepseek/deepseek-v4-flash", seed=101)
    accepted = await extractor.extract_relations(packets)
    snap = extractor.snapshot()
    print(f"\naccepted relations              : {len(accepted)}")
    print(f"fallback_no_method              : {snap['fallback_no_method']}/{len(packets)}")
    print(f"fallback_detected_method        : {snap['fallback_detected_method']}/{len(packets)}")
    print(f"structural_neutrals_no_call     : {snap['structural_neutrals_no_call']}")
    print(f"generation_failures             : {snap['generation_failures']}")
    print(f"invalidates_arm                 : {snap['invalidates_arm']}")
    print(f"config tag                      : {__import__('experiments.worker_replacement.arm3_relations', fromlist=['x']).ARM3_EXTRACTOR_CONFIG_TAG}")
    raw = [a for a in snap["comparison_audit"] if a.get("fallback_no_method")]
    print(f"\nrecords with raw text retained  : {len(raw)}/{len(packets)}")
    if accepted:
        print("\nUNEXPECTED: accepted relations from failure notices:")
        for r in accepted:
            print("  ", r.model_dump(mode="json"))

asyncio.run(main())
