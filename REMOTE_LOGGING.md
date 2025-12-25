# Remote Logging with PolyLog

PolyLog now supports streaming logs to Supabase in real-time, matching the functionality of the Swift LogRemote implementation!

## Setup

### 1. Create the Supabase table

Run the migration SQL from `polykit-swift/Documentation/Migrations/logs_table.sql` in your Supabase SQL editor to create the `polylogs` table with proper indexes and realtime support.

### 2. Set environment variables

```bash
export POLYLOG_APP_ID="my-awesome-app"
export POLYLOG_SUPABASE_URL="https://xyz.supabase.co"
export POLYLOG_SUPABASE_KEY="your-anon-key"
# Optional: Override table name (defaults to "polylogs")
export POLYLOG_TABLE="polylogs"
```

### 3. Use it in your code

```python
from polykit.log import PolyLog

# Enable remote logging with a single parameter
logger = PolyLog.get_logger(remote=True)

# Logs now stream to Supabase in real-time!
logger.info("Application started")
logger.debug("Debug information")
logger.error("Something went wrong")
```

## How It Works

- **Buffered**: Logs are buffered in memory (max 10 entries or 0.15s)
- **Background thread**: All network operations happen in a background thread
- **Best-effort**: If network fails, logs are dropped (no blocking, no retry)
- **Fast**: Matches Swift implementation's ~100-250ms streaming performance
- **Device tracking**: Stable device ID based on MAC address (with ULID fallback)
- **Session tracking**: Each process run gets a unique session ID

## Schema

Logs are stored with:

- `id`: ULID (time-sortable, generated from log timestamp)
- `timestamp`: When the log was created
- `level`: debug, info, warning, error, critical
- `message`: The log message
- `device_id`: Stable device identifier
- `app_bundle_id`: Your app identifier (from `POLYLOG_APP_ID`)
- `session_id`: Unique per process run
- `group_identifier`: Logger name (optional)
- `created_at`: When inserted into Supabase

## Example: Viewing Logs

You can now use your Swift log viewer app to see Python logs streaming in real-time alongside your Swift app logs!

```python
# Python app
logger = PolyLog.get_logger("DataProcessor", remote=True)
logger.info("Processing started")
logger.info("Processed 1000 records")
logger.info("Processing complete")
```

All these logs will appear in your log viewer with ~100-250ms latency. 🚀

## ULID Support

Python PolyKit now includes ULID generation matching the Swift implementation:

```python
from polykit.core import ULID, generate_ulid

# Generate a ULID (convenience function)
ulid = generate_ulid()  # e.g., "01ARZ3NDEKTSV4RRFFQ69G5FAV"

# Generate for a specific datetime
from datetime import datetime
ulid = ULID.generate(datetime(2024, 1, 1))

# Decode a ULID
decoded = ULID.decode(ulid)
print(decoded.timestamp_ms)  # Milliseconds since epoch
print(decoded.random_bytes)  # 10 bytes of randomness

# Monotonic generation (guaranteed increasing)
from polykit.core import get_ulid_generator

generator = get_ulid_generator()
ulid1 = generator.next()
ulid2 = generator.next()  # Always sorts after ulid1
```

## Migration Notes

If you're using environment variables in production:

- Add the three required env vars to your deployment config
- No code changes needed if already using `PolyLog.get_logger()`
- Just add `remote=True` to enable streaming
- Missing env vars? A warning prints to stderr, logging continues normally

## Performance

Remote logging adds minimal overhead:

- Logs are buffered and sent in batches
- Network operations happen on a background thread
- No blocking of main application flow
- Failed network requests are logged to stderr but don't crash

Perfect for development, staging, and production monitoring!
