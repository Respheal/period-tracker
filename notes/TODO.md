# To Do items:

## Stack

- [ ] Set up Redis docker container

## Users

### References

- https://medium.com/@ancilartech/bulletproof-jwt-authentication-in-fastapi-a-complete-guide-2c5602a38b4f
- https://fastapi.tiangolo.com/tutorial/security/

### Authentication

- [ ] Function to generate access tokens (15 min)
- [ ] Access token contains scopes (user:read, user:write, user:manage, admin same?)
- [ ] Access token stored in memory or sessionStorage (NEVER in localStorage)
- [ ] Function to generate refresh tokens (7 days)
- [ ] Refresh token stored in HTTP-only cookie with SameSite attribute (strict or lax). Example:

```python
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=60 * 60 * 24 * settings.REFRESH_TOKEN_EXPIRE_DAYS  # in seconds
    )
```

- [ ] Endpoint to create a user
- [ ] Endpoint to provide a password and receive both tokens
- [ ] Access token stored in authorization header (automatic for fastapi)
- [ ] Access token is validated by signature, expiration, and scopes for the request
- [ ] Endpoint to log out(?)
- [ ] Endpoint to issue new tokens using the refresh token
- [ ] Using a refresh token stores its jti in redis to blacklist reuse
- [ ] In React, if an api request with an access token fails for token expiration, refresh the token
- [ ] Configure RS256 (min 2048 bits)
- [ ] Configure CORS policies

## User Data Model

- [ ] Name
- [ ] Password (hashed)
- [ ] Average menses length (average period length in days)
- [ ] Average cycle length (average time between period start dates)

### User UI functionality

- [ ] User creation page
- [ ] User login page
- [ ] User settings page

### Calendar functionality

- [ ] Log Model (One user can have many logs)
  - Log objects are of type menstruation or symptom
- [ ] Endpoint to create an menstrual event (period start date)
  - Start Date (required)
  - End Date (Optional)
  - If End Date is null,
- [ ] Endpoint to update a menstrual event (update the end date)
- [ ] Endpoint to create a symptom event
  - Flow intensity (none, spotting, light, medium, heavy; int: 0-4)
  - Symptoms (none, cramps, headache, bloating, acne, hot flashes, back pain, tender breasts; list[str]?)
  - Mood (none, annoyed, anxious, energized, happy, sad, stressed, fatigued)
  - Ovulation test (none, positive, negative)
  - Discharge (none, creamy, )

### Calendar UI

- [ ] Display events in calendar format ()
