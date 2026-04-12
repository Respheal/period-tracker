import { createFileRoute } from '@tanstack/react-router';

import {
  Container,
  Box,
  Grid,
  Center,
  GridItem,
  DatePicker,
  Tabs,
  Heading,
} from '@chakra-ui/react';
import dayjs from 'dayjs';
import type { Period, Response, SymptomEvent, Temperature } from '@/client/types.gen';

import Logo from '@/components/Logo';
import { DatePickerDayTable } from '@/components/day-table';

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
    <Container
      fluid
      centerContent={true}
      maxWidth={{ base: '100dvw', md: '90dvw', lg: '3xl' }}>
      <Logo />
      <Grid
        w='full'
        mt={{ base: 5, md: 10 }}
        templateColumns={{ base: '1fr', md: '{sizes.60} 1fr' }}
        gap={{ base: 1, md: 2 }}>
        {/* Log Event */}
        <GridItem>
          <Box p={2} height='full' borderWidth='1px' borderColor='border.inverted'>
            <Heading>Log Event</Heading>
            <Tabs.Root variant='plain'>
              <Tabs.List bg='bg.muted' rounded='l3' p='1'>
                <Tabs.Trigger value='foo'>aaa</Tabs.Trigger>
                <Tabs.Trigger value='bar'>bbb</Tabs.Trigger>
                <Tabs.Indicator />
              </Tabs.List>
              <Tabs.Content value='foo'>hewwo? mr obama?</Tabs.Content>
              <Tabs.Content value='bar'>cursed</Tabs.Content>
            </Tabs.Root>
          </Box>
        </GridItem>
        {/* Data */}
        <GridItem>
          <Box p={2} height='full' borderWidth='1px' borderColor='border.inverted'>
            <Heading>Cycle Data??</Heading>
          </Box>
        </GridItem>
        {/* Calendar */}
        <GridItem
          rowSpan={{ base: 1, md: 2 }}
          colStart={{ base: 1, md: 2 }}
          rowStart={{ base: 3, md: 1 }}>
          <Box p={2} borderWidth='1px' borderColor='border.inverted'>
            <Center>
              <DatePicker.Root readOnly inline>
                <DatePicker.Content unstyled>
                  <DatePicker.View view='day'>
                    <DatePicker.Header />
                    <DatePickerDayTable events={mockEvents} />
                  </DatePicker.View>
                  <DatePicker.View view='month'>
                    <DatePicker.Header />
                    <DatePicker.MonthTable />
                  </DatePicker.View>
                  <DatePicker.View view='year'>
                    <DatePicker.Header />
                    <DatePicker.YearTable />
                  </DatePicker.View>
                </DatePicker.Content>
              </DatePicker.Root>
            </Center>
          </Box>
        </GridItem>
        {/* Graph */}
        <GridItem colSpan={{ base: 1, md: 2 }}>
          <Box p={2} borderWidth='1px' borderColor='border.inverted'>
            aaaaa
          </Box>
        </GridItem>
      </Grid>
    </Container>
  );
}
