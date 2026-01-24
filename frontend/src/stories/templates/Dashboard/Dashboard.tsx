import { Container, Grid, Paper } from "@mui/material";
import PeriodLogger from "../../organisms/PeriodLogger/PeriodLogger";
import { DateCalendar } from "@mui/x-date-pickers/DateCalendar";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";

export default function Dashboard() {
  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Container>
        <Grid container spacing={2}>
          {/* Calendar Row */}
          <Grid size={7}>
            <Paper>
              <DateCalendar />
            </Paper>
          </Grid>
          <Grid container size={5} spacing={1}>
            <Grid>
              <Paper>
                <PeriodLogger />
              </Paper>
            </Grid>
            <Grid>
              <Paper>
                <PeriodLogger />
              </Paper>
            </Grid>
            <Grid>
              <Paper>
                <PeriodLogger />
              </Paper>
            </Grid>
          </Grid>
        </Grid>
      </Container>
    </LocalizationProvider>
  );
}
