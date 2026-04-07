import PeriodLogger from '../../organisms/PeriodLogger/PeriodLogger';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import Calendar from '../../molecules/CycleCalendar/Calendar';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';

export default function Dashboard() {
  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Box maxWidth='sm'>
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
      </Box>
    </LocalizationProvider>
  );
}
