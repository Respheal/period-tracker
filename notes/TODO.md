# To Do items:

## Code References

- https://medium.com/@ancilartech/bulletproof-jwt-authentication-in-fastapi-a-complete-guide-2c5602a38b4f
- https://fastapi.tiangolo.com/tutorial/security/
- https://freedium-mirror.cfd/https://medium.com/@letscodefuture/implementing-end-to-end-encryption-in-a-react-application-a-beginners-guide-08b846353d19
- https://escape.tech/blog/how-to-secure-fastapi-api/
- https://www.freecodecamp.org/news/best-practices-for-security-of-your-react-js-application/
- https://medium.com/@pdlsandesh144/a-step-by-step-guide-on-using-node-js-to-implement-two-factor-authentication-059c7bcb220c
- [EMA Ref](https://stackoverflow.com/questions/12636613/how-to-calculate-moving-average-without-keeping-the-count-and-data-total)
- https://auth0.com/blog/rs256-vs-hs256-whats-the-difference/
- https://www.bestpractices.dev/en/criteria/0

## Accessibility References

- https://www.w3.org/WAI/ARIA/apg/example-index/
- https://www.w3.org/TR/using-aria/#intro

## Similar Apps

- https://github.com/moncycle-app/backend-api-web-app
- https://bloodyhealth.gitlab.io/

## Discussions

- https://www.reddit.com/r/selfhosted/comments/1i26vii/developing_selfhosted_period_tracking/
- https://www.recurse.com/still-computing/issue-3
- https://www.alizaaufrichtig.com/period-tracker

## Documentation

- [ ] Wiki (or similar) on github

## CI

- [ ] Build and publish images (frontend and backend) to GH repo
- [ ] Semantic versioning of releases
- [x] Flake, Mypy, and Ruff checks

## Testing

- [ ] Accesssibility testing (Ladle?)

### Stack

- [x] Set up Redis docker container
- [ ] Automatic data backup?
- [ ] Configure traefik, enforce https

## Backend

### Backend Bugs and Improvements

Things that came up while working on the authentication flow on the frontend:

- [ ] Anyone can register as an admin
  - This was sort of intended at the start, since this was meant to be installed on a a
    private machine and shared by only a few users, but the ability to register anyone as
    an admin undermines the partners feature
- [ ] Speaking of the partners features, it's currently set up backwards: A user picks
      whose data they can access, rather than a user allowing a partner to access it.
- [ ] The frontend will require a fresh token for critical actions like changing the
      password, but the backend doesn't. The backend should block password change requests
      from a not-fresh token. The frontend will also require a fresh token, and therefore
      should never send a refreshed token to the backend in the first place.
- [ ] POST /auth/logout, because there should be a way to expire tokens that isn't
      refreshing them
- [ ] valid_after timestamp on tokens, bumped on password changes or when an account is
      disabled/enabled. Have /auth/refresh reject older tokens

### Framework

- [x] FastAPI
- [x] SQLModel
- [x] SQLite
- [x] Pytest + Coverage
- [x] Pydantic Settings

### Users

#### User Data Model

- [x] Username
- [x] Display Name
- [x] Password (hashed)
- [x] Average menses length (average period length in days) (separate model)
- [x] Average cycle length (average time between period start dates) (separate model)
- [x] Partners (List of users with access to this User's calendar, many-many)
  - [ ] Period Only option (only displays the user's period dates and stats for the
        partner), not the temp or cycle data.

#### User Stats

- [x] Endpoint to retrieve user stats
  - Median and Mean period length (exponential moving average)
  - Median and mean cycle length (exponential moving average)
  - Median and mean temperature (exponential moving average)

#### Authentication

- [x] Function to generate access tokens (15 min)
- [x] Function to generate refresh tokens (7 days)
- [x] Endpoint to create a user
- [x] Endpoint to provide a password and receive both tokens
- [x] Access token stored in authorization header (automatic for fastapi)
- [x] Access token is validated by signature, expiration
- [x] Endpoint to issue new tokens using the refresh token
- [x] Using a refresh token stores its jti in redis to blacklist reuse
- [x] Configure RSA256 (min 2048 bits)
- [x] Configure CORS policies
- [ ] (New) Refresh Token Intervals
  - Removes the Locks requirement from renewing refresh tokens
- [ ] (New) Refresh Token Families (and family revocation); revoke entire family on token
      replay outside interval
- [ ] Offer Single Sign On via OAuth/OIDC as an _option_ (Signing in with Google defeats
      the point imo)
- [ ] Rate limiting on login (long term, post-release maybe)

### Events

- [x] Endpoint to retrieve all events
  - User.id
  - Date Range
  - Event Type
  - Skip/Limit (default: 0/100)
  - Also display count (refer to Netbox's API response)
- [x] Endpoint to retrieve all events as csv
  - Same filters as above

#### Period Events

- [x] Period Model
  - Start Date (required)
  - End Date (Optional)
  - Length (Optional, updated when both start/end known)
  - User.id
- [x] Endpoint to create an menstrual event (period start date)
  - Start Date updates the User median and mean period length (exponential moving average)
  - State+End updates the User median and mean cycle length (exponential moving average)
- [x] Endpoint to retrieve all mentrual events
  - Filter by:
    - Date Range
    - Length
    - Skip/Limit (default: 0/100)
    - Also display count (refer to Netbox's API response)
- [x] Endpoint to retrieve mentrual events as CSV (ref:
      https://medium.com/@liamwr17/supercharge-your-apis-with-csv-and-excel-exports-fastapi-pandas-a371b2c8f030)
  - Same filters as above
- [x] Endpoint to retrieve a specific mentrual event
- [x] Endpoint to update a menstrual event (e.g. update the end date)
- [x] Endpoint to delete a menstrual event

#### Symptom Events

- [x] Symptom Event Model
  - User.id
  - Datetime (required)
  - Flow intensity (none, spotting, light, medium, heavy; int: 0-4)
  - Symptoms (none, cramps, headache, bloating, acne, hot flashes, back pain, tender
    breasts, high libido, custom; list[str]?)
  - Mood (none, annoyed, anxious, energized, happy, sad, stressed, fatigued)
  - Ovulation test (none, positive, negative)
  - Discharge (none, creamy, sticky, unusual)
  - Sex (protected, unprotected, morning-after pill)
- [x] Endpoint to retrieve all symptom events
  - Filter by:
    - Date Range
    - Symptom (list[str], and\_)
    - Skip/Limit (default: 0/100)
    - Also display count (refer to Netbox's API response)
- [x] Endpoint to retrieve symptom events as CSV
  - Same filters as above
- [x] Endpoint to retrieve a specific symptom event
- [x] Endpoint to create a symptom event
- [x] Endpoint to update a symptom event
- [x] Endpoint to delete a symptom event

#### Temperature Events

- [x] Temperature Event Model
  - User.id
  - Datetime (required)
  - Reading (convert to C for storage)
- [x] Endpoint to retrieve all temperature events
  - Filter by:
    - Date Range
    - Skip/Limit (default: 0/100)
    - Also display count (refer to Netbox's API response)
- [x] Endpoint to retrieve temperature events as CSV
  - Same filters as above
- [x] Endpoint to retrieve a specific temperature event
- [x] Endpoint to create a temperature event
- [x] Endpoint to update a temperature event
- [x] Endpoint to delete a temperature event

## Frontend

### Framework

- [x] [Vite + React](https://react.dev/learn/build-a-react-app-from-scratch)
- [x] [Hey API](https://heyapi.dev/)
- [x] [TanStack Router](https://tanstack.com/router/latest) - routing? (consider form
      instead of hooks too)
- [x] [Chakra](https://chakra-ui.com/)
- [x] [TanStack Query](https://tanstack.com/query/latest) - API client, state handling
- [x] [Form Management](https://tanstack.com/form/latest)
- [ ] [Unit/Integration: Vitest + React Testing Library](https://vitest.dev/guide/browser/component-testing.html#testing-library-integration)
- [ ] [E2E Tests: Playwright](https://playwright.dev/)
- [ ] [Day.js](https://github.com/iamkun/dayjs) - If we need better date parsing on the
      frontend

### User UI functionality

- [ ] User creation page
- [ ] User login page
  - [ ] Access token stored in memory or sessionStorage (NEVER in localStorage)
  - [ ] Access token sent to API in authorization header (automatic for fastapi)
  - [ ] Refresh token stored in HTTP-only cookie with SameSite attribute (strict or lax).
  - [ ] An unauthorized response triggers creating a new token from the refresh token
- [ ] User log out (remove both tokens)
- [ ] User settings page

### Calendar UI

- [ ] Display symptom events in calendar
- [ ] Display period event as a multi-day event
  - If the event has end_date=null, create an estimation element with the ema length
    applied)
- [ ] Display fertile window estimate

## Stats UI

- [ ] Display User Stats
- [ ] Cycle length over time
- [ ] Mentrual length over time
- [ ] Temperature over time
