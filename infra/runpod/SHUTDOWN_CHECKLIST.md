# Shutdown checklist

- Stop all inference processes and confirm both validation passes have completed or have a verified resumable cache.
- Run `verify_resume.sh`; investigate every hash or cache-key failure before export.
- Run `export_results.sh` to a persistent path and copy the export off the Pod.
- Verify the exported manifest and SHA-256 inventory on the destination system.
- Preserve `/workspace/environment`, raw bounded observations, compiler results, logs, and acquisition provenance.
- Confirm no model weight, generated image, cache, raw output, or annotation identity was added to Git.
- Terminate the Pod only after the persistent volume and external export are verified. Remove the volume later only through an explicit, separately reviewed retention decision.
