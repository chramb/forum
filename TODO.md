# TODOs
- [ ] make `*.sql` functions for each request and execute those
- [ ] organize routers (with `__init__.py`'s)
- [ ] get mock data for users, and posts (ChatGPT)
- [ ] figure out search and optional parameters
- [ ] ban users delete tags (with cascade delete or [anon] posts)
- [ ] figure out http login (wrapper for easier replacement later?)
- [ ] Full Text Search w/ materialized view -> trigger to update
- [ ] Notifications

## Quality of Life
- [ ] `server/util/config.py` - load dotenv if var missing, and support defaults
- [ ] UI with renderer (jinja2)
- [ ] tags removed automatically when 0 posts