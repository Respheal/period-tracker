import { createFileRoute } from '@tanstack/react-router';

import { Box, Grid, Center, GridItem, Tabs, Heading } from '@chakra-ui/react';
import dayjs from 'dayjs';
import type { Period, Response, SymptomEvent, Temperature } from '@/client/types.gen';

import { EventCalendar } from '@/components/EventCalendar';
import { LogPeriod } from '@/components/EventForm';

export const Route = createFileRoute('/dashboard')({
  component: RouteComponent,
});

const mockSymptoms: SymptomEvent[] = [
  {
    user_id: '1',
    flow_intensity: '2',
    sex: ['protected'],
    mood: ['big mad'],
    ovulation_test: true,
    discharge: ['terrible', 'gross'],
    date: dayjs().toDate(),
    symptoms: ['tummy hurt', 'headache', 'everything bad', 'aaaaaaaaaaaaaaaaa'],
  },
  {
    user_id: '1',
    flow_intensity: '0',
    sex: null,
    mood: ['big mad'],
    ovulation_test: false,
    discharge: null,
    date: dayjs().add(1, 'day').toDate(),
    symptoms: null,
  },
  {
    user_id: '1',
    flow_intensity: '0',
    sex: null,
    mood: null,
    ovulation_test: true,
    discharge: null,
    date: dayjs().add(5, 'day').toDate(),
    symptoms: null,
  },
  {
    user_id: '1',
    flow_intensity: '0',
    sex: null,
    mood: ['weh'],
    ovulation_test: false,
    discharge: null,
    date: dayjs().add(5, 'day').toDate(),
    symptoms: null,
  },
];

const mockPeriods: Period[] = [
  {
    user_id: '1',
    start_date: dayjs().toDate(),
    end_date: dayjs().add(3, 'day').toDate(),
  },
];

const mockTemps: Temperature[] = [
  {
    user_id: '1',
    temperature: 32.0,
    timestamp: dayjs().toDate(),
  },
  {
    user_id: '1',
    temperature: 31.2,
    timestamp: dayjs().toDate(),
  },
  {
    user_id: '1',
    temperature: 31.0,
    timestamp: dayjs().add(1, 'day').toDate(),
  },
];

const mockEvents: Response = {
  count: 4,
  data: { symptoms: mockSymptoms, periods: mockPeriods, temperatures: mockTemps },
};

function RouteComponent() {
  return (
    <Grid
      w='full'
      templateColumns={{ base: '1fr', md: '{sizes.80} 1fr' }}
      gap={{ base: 1, md: 2 }}>
      {/* Log Event */}
      <GridItem>
        <Box p={2} height='full' borderWidth='1px' borderRadius='md'>
          <Tabs.Root
            fitted
            lazyMount
            unmountOnExit
            variant='enclosed'
            maxW='md'
            defaultValue={'period'}>
            <Tabs.List bg='bg.muted' rounded='l3' p='1'>
              <Tabs.Trigger value='period'>Period</Tabs.Trigger>
              <Tabs.Trigger value='symptoms'>Symptoms</Tabs.Trigger>
              <Tabs.Trigger value='temperature'>Temperature</Tabs.Trigger>
              <Tabs.Indicator />
            </Tabs.List>
            <Tabs.Content value='period'>
              <LogPeriod />
            </Tabs.Content>
            <Tabs.Content value='symptoms'>another tab</Tabs.Content>
            <Tabs.Content value='temperature'>cursed</Tabs.Content>
          </Tabs.Root>
        </Box>
      </GridItem>
      {/* Data */}
      <GridItem rowStart={{ base: 3, md: 2 }}>
        <Box p={2} height='full' borderWidth='1px' borderRadius='md'>
          <Heading>Cycle Data??</Heading>
        </Box>
      </GridItem>
      {/* Calendar */}
      <GridItem
        rowSpan={{ base: 1, md: 2 }}
        colStart={{ base: 1, md: 2 }}
        rowStart={{ base: 2, md: 1 }}>
        <Box p={2} borderWidth='1px' borderRadius='md'>
          <Center>
            <EventCalendar events={mockEvents} />
          </Center>
        </Box>
      </GridItem>
      {/* Graph */}
      <GridItem colSpan={{ base: 1, md: 2 }}>
        <Box p={2} borderWidth='1px' borderRadius='md'>
          aaaaaa
        </Box>
      </GridItem>
    </Grid>
  );
}
