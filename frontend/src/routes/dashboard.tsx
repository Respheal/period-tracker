import { createFileRoute } from '@tanstack/react-router';

import {
  Container,
  Box,
  GridItem,
  DatePicker,
  Tabs,
  Heading,
  SimpleGrid,
} from '@chakra-ui/react';

import Logo from '@/components/Logo';

export const Route = createFileRoute('/dashboard')({
  component: RouteComponent,
});

function RouteComponent() {
  return (
    <Container centerContent={true}>
      <SimpleGrid columns={{ base: 1, md: 3 }} gap={{ base: 1, md: 2 }}>
        {/* Log Event */}
        <GridItem colSpan={{ base: 3, md: 1 }}>
          <Box height='full' borderWidth='1px' borderColor='border.inverted'>
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
        <GridItem colSpan={{ base: 3, md: 1 }}>
          <Box height='full' borderWidth='1px' borderColor='border.inverted'>
            <Heading>Cycle Data??</Heading>
          </Box>
        </GridItem>
        {/* Calendar */}
        <GridItem
          colSpan={{ base: 3, md: 2 }}
          rowSpan={{ base: 1, md: 2 }}
          colStart={{ base: 1, md: 2 }}
          rowStart={{ base: 3, md: 1 }}>
          <Box borderWidth='1px' borderColor='border.inverted'>
            <Logo />
            <DatePicker.Root selectionMode='range' inline width='fit-content'>
              <DatePicker.Content unstyled>
                <DatePicker.View view='day'>
                  <DatePicker.Header />
                  <DatePicker.DayTable />
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
          </Box>
        </GridItem>
        {/* Graph */}
        <GridItem colSpan={3}>
          <Box borderWidth='1px' borderColor='border.inverted'>
            aaaaa
          </Box>
        </GridItem>
      </SimpleGrid>
    </Container>
  );
}
