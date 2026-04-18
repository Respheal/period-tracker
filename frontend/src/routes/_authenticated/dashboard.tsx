import { createFileRoute } from '@tanstack/react-router';
import { Box, Grid, Center, GridItem, Tabs, Heading } from '@chakra-ui/react';

import { EventCalendar } from '@/components/EventCalendar';
import { LogPeriod } from '@/components/EventForm';

export const Route = createFileRoute('/_authenticated/dashboard')({
  component: RouteComponent,
});

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
            <EventCalendar />
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
