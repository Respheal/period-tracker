import {
  useDisclosure,
  Drawer,
  Button,
  Portal,
  CloseButton,
  Icon,
} from '@chakra-ui/react';
import { LuMenu } from 'react-icons/lu';
import { MenuLinks } from './MenuLinks';

export function MobileDrawer({
  nav_items = [],
  logoutFn,
}: {
  nav_items: readonly (readonly [string, string])[];
  logoutFn: () => void;
}) {
  const { open, onToggle } = useDisclosure();

  return (
    <Drawer.Root open={open} onOpenChange={onToggle} size='xs' placement={'start'}>
      <Drawer.Trigger asChild>
        <Button variant='outline' size='sm'>
          <Icon>
            <LuMenu />
          </Icon>
        </Button>
      </Drawer.Trigger>
      <Portal>
        <Drawer.Backdrop />
        <Drawer.Positioner>
          <Drawer.Content>
            <Drawer.Header>
              <Drawer.Title>Navigation</Drawer.Title>
            </Drawer.Header>
            <Drawer.Body>
              <MenuLinks nav_items={nav_items} isMobile logoutFn={logoutFn} />
            </Drawer.Body>
            <Drawer.CloseTrigger asChild>
              <CloseButton size='md' />
            </Drawer.CloseTrigger>
          </Drawer.Content>
        </Drawer.Positioner>
      </Portal>
    </Drawer.Root>
  );
}
