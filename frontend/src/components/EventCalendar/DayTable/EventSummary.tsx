'use client';

import type { JSX } from 'react';
import { Badge, Circle, Wrap, DataList, For, Stack } from '@chakra-ui/react';

import { type SymptomEvent } from '@/client/types.gen';

interface EventSummary {
  symptoms: string[];
  mood: string[];
  flowIntensity: number;
  ovulationTest: boolean;
  discharge: string[];
  sex: string[];
}

export function EventSummary(events: SymptomEvent[]): (JSX.Element | undefined)[] {
  const summary = summarizeSymptomEvents(events);
  let symptomNode: JSX.Element | undefined = undefined;
  let moodNode: JSX.Element | undefined = undefined;
  let flowIntensityNode: JSX.Element | undefined = undefined;
  let ovulationTestNode: JSX.Element | undefined = undefined;
  let dischargeNode: JSX.Element | undefined = undefined;
  let sexNode: JSX.Element | undefined = undefined;

  if (summary.symptoms.length > 0) {
    symptomNode = (
      <DataList.Item key='symptoms' alignItems={'flex-start'}>
        <DataList.ItemLabel>Symptoms</DataList.ItemLabel>
        <DataList.ItemValue>{formatBadgeList(summary.symptoms)}</DataList.ItemValue>
      </DataList.Item>
    );
  }
  if (summary.mood.length > 0) {
    moodNode = (
      <DataList.Item key='mood' alignItems={'flex-start'}>
        <DataList.ItemLabel>Mood</DataList.ItemLabel>
        <DataList.ItemValue>{formatBadgeList(summary.mood)}</DataList.ItemValue>
      </DataList.Item>
    );
  }
  if (summary.flowIntensity > 0) {
    const icons = Array.from({ length: summary.flowIntensity }, (_, i) => (
      <Circle key={i} bg='red' size={3.5} />
    ));
    flowIntensityNode = (
      <DataList.Item key='flow-intensity'>
        <DataList.ItemLabel>Flow Intensity</DataList.ItemLabel>
        <DataList.ItemValue>
          <Stack direction={'row'} gap={1}>
            {icons}
          </Stack>
        </DataList.ItemValue>
      </DataList.Item>
    );
  }
  if (typeof summary.ovulationTest !== 'undefined') {
    ovulationTestNode = (
      <DataList.Item key='ovulation-test'>
        <DataList.ItemLabel>Ovulation Test</DataList.ItemLabel>
        <DataList.ItemValue>
          <Badge colorPalette={summary.ovulationTest ? 'green' : 'gray'}>
            {summary.ovulationTest ? 'Positive' : 'Negative'}
          </Badge>
        </DataList.ItemValue>
      </DataList.Item>
    );
  }
  if (summary.discharge.length > 0) {
    dischargeNode = (
      <DataList.Item key='discharge' alignItems={'flex-start'}>
        <DataList.ItemLabel>Discharge</DataList.ItemLabel>
        <DataList.ItemValue>{formatBadgeList(summary.discharge)}</DataList.ItemValue>
      </DataList.Item>
    );
  }
  if (summary.sex.length > 0) {
    sexNode = (
      <DataList.Item key='sex' alignItems={'flex-start'}>
        <DataList.ItemLabel>Sex</DataList.ItemLabel>
        <DataList.ItemValue>{formatBadgeList(summary.sex)}</DataList.ItemValue>
      </DataList.Item>
    );
  }
  return [
    symptomNode,
    moodNode,
    flowIntensityNode,
    ovulationTestNode,
    dischargeNode,
    sexNode,
  ];
}

/**
 * Map all events into simplified and combined lists
 * @param events An array of SymptomEvent objects to be formatted
 * @returns An EventSummary object summarizing the provided events
 */
function summarizeSymptomEvents(events: SymptomEvent[]): EventSummary {
  const symptoms = [...new Set(events.flatMap((obj) => obj.symptoms || []))];
  const mood = [...new Set(events.flatMap((obj) => obj.mood || []))];
  const flowIntensity = Math.max(
    ...events.map((event) => parseInt(event.flow_intensity || '0')),
  );
  const ovulationTest = events.some(
    (event) => event.ovulation_test && event.ovulation_test === true,
  );
  const discharge = [...new Set(events.flatMap((obj) => obj.discharge || []))];
  const sex = [...new Set(events.flatMap((obj) => obj.sex || []))];
  return { symptoms, mood, flowIntensity, ovulationTest, discharge, sex };
}

function formatBadgeList(items: string[]) {
  return (
    <Wrap align='top'>
      <For each={items}>
        {(item, index) => (
          <Badge key={index} size='md' variant='surface'>
            {item}
          </Badge>
        )}
      </For>
    </Wrap>
  );
}
