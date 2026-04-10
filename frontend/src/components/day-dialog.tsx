import { Popover } from '@chakra-ui/react';

export const DayPopover = (weh: string) => {
  return (
    <Popover.Root lazyMount unmountOnExit>
      <Popover.Trigger />
      <Popover.Positioner>
        <Popover.Content>
          <Popover.CloseTrigger />
          <Popover.Arrow>
            <Popover.ArrowTip />
          </Popover.Arrow>
          <Popover.Body>
            <Popover.Title />
          </Popover.Body>
        </Popover.Content>
      </Popover.Positioner>
    </Popover.Root>
  );
};
