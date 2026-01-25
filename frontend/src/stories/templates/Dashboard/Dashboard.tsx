import { Container, Grid, Paper, Stack } from "@mui/material";
import PeriodLogger from "../../organisms/PeriodLogger/PeriodLogger";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import Calendar from "../../molecules/CycleCalendar/Calendar";

export default function Dashboard() {
  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Container fixed maxWidth="sm" disableGutters>
        <Grid container spacing={2}>
          {/* Calendar Row */}
          <Grid size={{ xs: 12, md: 7 }}>
            <Paper>
              <Calendar />
            </Paper>
          </Grid>
          <Grid container size={{ xs: 12, md: 5 }}>
            <Stack spacing={2}>
              <Paper>
                <PeriodLogger />
              </Paper>
              <Paper>
                <PeriodLogger />
              </Paper>
              <Paper>
                <PeriodLogger />
              </Paper>
            </Stack>
          </Grid>
        </Grid>
      </Container>
    </LocalizationProvider>
  );
}
