# API Guild

Barbell's endpoints are public facing, so should work to follow common conventions.

## What

Endpoints should be RESTful, or at least folow RESTful ideas. All endpoints should have ratelimiting, a return type ,and security if possible.

### Main Pitfalls

Here are some of the most common errors when writing RESTful APIs:

[Source](https://stackoverflow.blog/2020/03/02/best-practices-for-rest-api-design/)

#### Perfer JSON where possible

Avoid other formats like XML. Use form data for data and files, but JSON wherever possible

#### Use nouns instead of verbs in endpoint paths

Instead of createing new URLs for `GET`, `POST`, `PUT`, and `DELETE`, just use one common URL with diffrent `HTTP` methods.

#### Use the correct HTTP methods

* GET retrieves resources.
* POST submits new data to the server.
* PUT updates existing data.
* DELETE removes data.

Each of these map to CRUD opperations:

| CRUD | HTTP |
|------|------|
| Create | POST, PUT if we don't have `id` or `uuid` |
| Read | GET | 
| Update | PUT to replace, PATCH to modify |
| Delete | DELETE |

#### Use the correct errors

* 400 Bad Request - This means that client-side input fails validation.
* 401 Unauthorized - This means the user isn't not authorized to access a resource. It usually returns when the user isn't authenticated.
* 403 Forbidden - This means the user is authenticated, but it's not allowed to access a resource.
* 404 Not Found - This indicates that a resource is not found.
* 500 Internal server error - This is a generic server error. It probably shouldn't be thrown explicitly.
* 502 Bad Gateway - This indicates an invalid response from an upstream server.
* 503 Service Unavailable - This indicates that something unexpected happened on server side (It can be anything like server overload, some parts of the system failed, etc.).

#### Allow filtering, sorting, and pagination

See source

## Where

If your endpoint is related to authentication in any way, put it in `auth_v1.py`. Otherwise, it belongs in the main API router. These endpoints go in the `v1` folder, and in specific sub files. You should be able to figure out which by their names. If none of them fit, add a new file with a router, and add that router to `router.py`
