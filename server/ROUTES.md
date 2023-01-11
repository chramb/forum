# Routes

## Questions:

> [!Note]\
> put idempotent - edit\
> post side effects - create

## `/api/v0/`
- `/`
  - [ ] `/@<username>` - get - preview
    - [ ] `/@<username>/ban` - delete - moderator+
    - [ ] `/@<username>/remove` - delete - admin+
    - [ ] `/@<username>/search` -> `/search` `WHERE username = ?{query}`
  - [ ] `/#<tag>` - get - preview
    - [ ] `/#<tag>/search`
    - [ ] `/#<tag>/remove` - delete - admin
  - `/auth`
  - [X] `/auth/register` - post
  - [ ] `/auth/login` - post
  - [ ] `/auth/logout` - post
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