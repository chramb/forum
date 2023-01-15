# Routes

## Questions:

> [!Note]\
> put idempotent - edit\
> post side effects - create

## `/api/v0/`
- `/`
  - [X] `/@<username>` - get - preview
    - [ ] `/@<username>/ban` - delete - moderator+
    - [ ] `/@<username>/remove` - delete - admin+
    - [ ] `/@<username>/search` -> `/search` `WHERE username = ?{query}`
  - [ ] `/tag/<tag>` - get - preview
    - [ ] `/tag/<tag>/search`
    - [ ] `/tag/<tag>/remove` - delete - admin
  - [ ] `/role/<role>` - get - preview
    - [ ] `/role/<role>/search`
    - [ ] `/role/<role>/remove` - delete - admin
  - `/auth`
  - [ ] `/auth/register` - post
  - [ ] `/auth/login` - post
  - [ ] `/auth/logout` - post
  - [ ] `/auth/status` - get
- `/post/`
  - post - create: submit -> redirect to `/post/<id>`
  - `/post/<id>`
    - [ ] get - preview
    - [ ] put - edit
    - [ ] delete - delete
    - `/post/<id>/comment`
      - post - create: submit -> redirect to `/post/<id>/comment/<id>`
      - `/post/<id>/comment/<id>/`
          - get - preview
          - put - edit
          - delete - delete
- `/account/`
  - `/account/settings`
  - `/account/posts`
  - `/account/comments`
- ``

- `/table/...` - get view

  >  **Everything same as `/api/` except:**
  > - query returns raw table,
  > - only get requests
  > - extra `?` parameters: (`?sort_by`, `?limit`(per page))