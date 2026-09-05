class JobCancelled(Exception):
    """Raised (from a pipeline checkpoint or a pyannote/whisper progress hook)
    when a user cancels a running job."""
