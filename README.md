# Fuser
Sample user CRUD system

## Usage

Clone code to local machine:

```shell
git clone git@github.com:alexbobrow/fuser.git
```

Prepare database:

```shell
docker compose run --rm web python manage.py migrate
```

Create staff user:

```shell
docker compose run --rm web python manage.py createsuperuser
```

Run the app:

```shell
docker compose up
```

Run tests:

```shell
docker compose run --rm web python manage.py tests
```

## API endpoints

### Overview

| Action                     | Request                               | Permissions     |
|:---------------------------|:--------------------------------------|:----------------|
| Create user                | `POST /user/`                         | Anybody         |
| List users                 | `GET /user/`                          | Staff           |
| Update user (all fields)   | `PUT /user/{id}`                      | Staff and owner |
| Update user (some fields)  | `PATCH /user/{id}`                    | Staff and owner |
| Update verification status | `POST /user/{id}/update-verification` | Staff           |
| Update account balance     | `POST /user/{id}/update-balance`      | Staff           |
| Delete user                | `DELETE /user/{id}`                   | Staff           |

### Create user

```
POST /user/
```

Available for all.

Fields:

| Param      | Type    | Is required |
|:-----------|:--------|:------------|
| username   | String  | Required    |
| email      | String  | Optional    |
| first_name | String  | Optional    |
| last_name  | String  | Optional    |
| city       | String  | Optional    |
| country    | String  | Optional    |

Response example:
```json
{
    "id": 2,
    "username": "username",
    "email": "",
    "first_name": "",
    "last_name": "",
    "city": "",
    "country": ""
}
```

Error response example:

```json
{
    "username": [
        "user with this Username already exists."
    ]
}
```

### List users

Used to list all existing accounts. Available to staff users.

```http request
GET /user/
```

Query params:

| Param       | Is required |
|:------------|:------------|
| is_verified | Optional    |
| username    | Optional    |

Filter by username example:

```http request
GET /user/?username=admin
```

Filter by verification status example:

```http request
GET /user/?is_verified=false
```

### Update user

Update all fields:

```http request
PUT /user/{id}
```

Available for staff users and account owners.

Fields:

| Param      | Type    | Is required |
|:-----------|:--------|:------------|
| email      | String  | Required    |
| first_name | String  | Required    |
| last_name  | String  | Required    |
| city       | String  | Required    |
| country    | String  | Required    |

Response example:
```json
{
    "id": 2,
    "username": "username",
    "email": "",
    "first_name": "",
    "last_name": "",
    "city": "",
    "country": ""
}
```

Update specific fields:

```http request
PATCH /user/{id}
```

Available for staff users and account owners.

Fields:

| Param      | Type    | Is required |
|:-----------|:--------|:------------|
| email      | String  | Optional    |
| first_name | String  | Optional    |
| last_name  | String  | Optional    |
| city       | String  | Optional    |
| country    | String  | Optional    |

Response example:
```json
{
    "id": 2,
    "username": "username",
    "email": "",
    "first_name": "",
    "last_name": "",
    "city": "",
    "country": ""
}
```

### Update verification status

```http request
POST /user/{id}/update-verification
```
Fields:

| Param | Type    | Is required |
|:------|:--------|:------------|
| value | Boolean | Required    |

Available to staff users.

Request example:

```json
{
    "value": true
}
```

### Update account balance

```http request
POST /user/{id}/update-balance
```
Fields:

| Param | Type    | Is required |
|:------|:--------|:------------|
| value | Integer | Required    |

Available to staff users. It is allowed to change balance of verified users only. Use positive value to top-up account
balance and negative to charge. 

Request example:

```json
{
    "value": 100
}
```

New account balance is received in response:

```json
{
    "value": 150
}
```

Error response example:

```json
{
    "detail": "User is not verified"
}
```

### Delete user

```http request
DELETE /user/{id}
```

Used to delete account. Available to staff users.
