---
title: "Authentication"
description: "Letting the backend know who you are"
---

<script lang="ts">
  import { CodeSwitch } from '$lib/components/docs'
</script>

# API Keys

API keys are the primary way of authenticating public API requests. An API
key consists of two parts: a username, and a 16 character key. Your API
looks like this:
```
{USERNAME}:{KEY}
```
To get your final key, just replace the placeholders with your actual
username and key.

## Getting your Key

To get your key, head to [settings](/dashboard/settings). Find the "API Key" section. Click "Get My Key", and copy the key you are given.

## Using your Key

Whenever you are submitting a request to the public API, you need to include your API key in a header called `x-api-auth`.

{#snippet apiJsCode()}
```js
const apiKey = "myUsername:myLongKeyGoesHere";

let response = await fetch(url, {
  method: "GET",
  headers: {
    "x-api-auth": apiKey,
});
```
{/snippet}

{#snippet apiPyCode()}
```python
import requests

api_key = "myUsername:myLongKeyGoesHere"
response = requests.get('my_endpoint', headers={"x-api-auth": api_key})
```
{/snippet}

<CodeSwitch tabs={[
  { label: 'JavaScript', content: apiJsCode },
  { label: 'Python', content: apiPyCode }
]} />  

# Best Practices

There are a number of best practices that need to be followed to protect your API key.

### Don't Share Your Key

Treat your key as a password. It belongs to you, and only you. Don't share it.

### Never Hardcode API Keys

If you are writing an app or script, **never** put your key directly in the code. Instep, put the key in a `.env` file and import the key into your code.

# Advanced

While API keys are great for the public API, a different approach is needed for the internal API. You will probably not need this API, unless you are developing ann app off of Barbell, or need some advanced data not found in the public API. To access this data, you need to authenticate using the OAuth2 Password Bearer Flow. There are a lot of details to this flow, but the basics are below.

## Token Request

First, you need to request a token. Everything for advanced authentication has a `/auth/v1/` path. For getting a token, you need to call `/auth/v1/token/`.

{#snippet tokenJsCode()}
```js
let username = "myUsername";
let password = "myPassword";

let response = await fetch("auth/v1/token", {
  method: "POST",
  headers: {
    "Content-Type": "application/x-www-form-urlencoded",
  },
  body: new URLSearchParams({
    username,
    password,
  }),
  credentials: "include",
});
```
{/snippet}

{#snippet tokenPyCode()}
```python
import requests

body = {"username": "myUsername", "password": "myPassword"}
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
response = requests.post("auth/v1/token", data=body, headers=headers)
```
{/snippet}

<CodeSwitch tabs={[
  { label: 'JavaScript', content: tokenJsCode },
  { label: 'Python', content: tokenPyCode }
]} />  

This gives you a JWT token in the form of a [HTTP-only cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies) named `access_token`. This cookie cannot be modified or read by JavaScript when used in the browser, making it ideal for storing JWT tokens.

## Using the Token

TODO HERE
