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
- [ ] Average menses length (average period length in days)
- [ ] Average cycle length (average time between period start dates)
- [ ] Partners (List of users with access to this User's calendar, many-many)
  - Period Only option (only displays the user's period dates and stats for the partner)

#### User Stats

- [ ] Endpoint to retrieve user stats
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
- [ ] Offer Single Sign On via OAuth/OIDC as an _option_ (Signing in with Google defeats the point imo)

### Events

- [ ] Endpoint to retrieve all events
  - User.id
  - Date Range
  - Event Type
  - Skip/Limit (default: 0/100)
  - Also display count (refer to Netbox's API response)
- [ ] Endpoint to retrieve all events as csv
  - Same filters as above

#### Period Events

- [x] Period Model
  - Start Date (required)
  - End Date (Optional)
  - Length (Optional, updated when both start/end known)
  - User.id
- [ ] Endpoint to create an menstrual event (period start date)
  - Start Date updates the User median and mean period length (exponential moving average)
  - State+End updates the User median and mean cycle length (exponential moving average)
- [ ] Endpoint to retrieve all mentrual events
  - Filter by:
    - Date Range
    - Length
    - Skip/Limit (default: 0/100)
    - Also display count (refer to Netbox's API response)
- [ ] Endpoint to retrieve mentrual events as CSV (ref: https://medium.com/@liamwr17/supercharge-your-apis-with-csv-and-excel-exports-fastapi-pandas-a371b2c8f030)
  - Same filters as above
- [ ] Endpoint to retrieve a specific mentrual event
- [ ] Endpoint to update a menstrual event (e.g. update the end date)
- [ ] Endpoint to delete a menstrual event

#### Symptom Events

- [x] Symptom Event Model
  - User.id
  - Datetime (required)
  - Flow intensity (none, spotting, light, medium, heavy; int: 0-4)
  - Symptoms (none, cramps, headache, bloating, acne, hot flashes, back pain, tender breasts, high libido, custom; list[str]?)
  - Mood (none, annoyed, anxious, energized, happy, sad, stressed, fatigued)
  - Ovulation test (none, positive, negative)
  - Discharge (none, creamy, sticky, unusual)
  - Sex (protected, unprotected, morning-after pill)
- [ ] Endpoint to retrieve all symptom events
  - Filter by:
    - Date Range
    - Symptom (list[str], and\_)
    - Skip/Limit (default: 0/100)
    - Also display count (refer to Netbox's API response)
- [ ] Endpoint to retrieve symptom events as CSV
  - Same filters as above
- [ ] Endpoint to retrieve a specific symptom event
- [ ] Endpoint to create a symptom event
- [ ] Endpoint to update a symptom event
- [ ] Endpoint to delete a symptom event

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
- [ ] Endpoint to retrieve temperature events as CSV
  - Same filters as above
  - I have a rough draft of this but I could probably do better
- [ ] Endpoint to retrieve a specific temperature event
- [x] Endpoint to create a temperature event
- [ ] Endpoint to update a temperature event
- [ ] Endpoint to delete a temperature event

## Frontend

### Framework

- [ ] [Vite + React](https://react.dev/learn/build-a-react-app-from-scratch)
- [ ] [TanStack Query](https://tanstack.com/query/latest) - API client, state handling
- [ ] [TanStack Router](https://tanstack.com/router/latest) - routing? (consider form instead of hooks too)
- [ ] [Ladle](https://ladle.dev/)
- [ ] [Ladle Accessibility](https://ladle.dev/docs/a11y)
- [ ] [Ladle Actions](https://ladle.dev/docs/actions)
- [ ] [Ladle Controls](https://ladle.dev/docs/controls)
- [ ] [Ladlbe Story Source](https://ladle.dev/docs/source)
- [ ] [Ladle Width](https://ladle.dev/docs/width)
- [ ] [Material UI](https://mui.com/material-ui/)
- [ ] [Form Management](https://react-hook-form.com/)
- [ ] [Unit/Integration: Vitest + React Testing Library](https://vitest.dev/guide/browser/component-testing.html#testing-library-integration)
- [ ] [E2E Tests: Playwright](https://playwright.dev/)
- [ ] [Day.js](https://github.com/iamkun/dayjs) - If we need better date parsing on the frontend

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
  - If the event has end_date=null, create an estimation element with the ema length applied)
- [ ] Display fertile window estimate

## Stats UI

- [ ] Display User Stats
- [ ] Cycle length over time
- [ ] Mentrual length over time
- [ ] Temperature over time
