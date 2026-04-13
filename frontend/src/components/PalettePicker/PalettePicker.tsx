import { ColorPicker, ColorSwatchMix, Grid, Popover, Portal } from '@chakra-ui/react';

export function PalettePicker({
  setPalette,
}: {
  setPalette: React.Dispatch<React.SetStateAction<string>>;
}) {
  return (
    <Popover.Root>
      <Popover.Trigger asChild>
        <ColorSwatchMix size='lg' items={swatches.slice(0, 4)} />
      </Popover.Trigger>
      <Portal>
        <Popover.Positioner>
          <Popover.Content maxWidth={'fit-content'}>
            <Popover.Arrow />
            <Popover.Body>
              <ColorPicker.Root>
                <ColorPicker.HiddenInput />
                <ColorPicker.SwatchGroup>
                  <Grid templateColumns='repeat(5, 1fr)' gap='2'>
                    {swatches.map((item) => (
                      <ColorPicker.SwatchTrigger key={item} value={item}>
                        <ColorPicker.Swatch
                          value={item}
                          onClick={() => {
                            setPalette(item);
                            localStorage.setItem('user-palette', item);
                          }}>
                          <ColorPicker.SwatchIndicator boxSize='3' bg='white' />
                        </ColorPicker.Swatch>
                      </ColorPicker.SwatchTrigger>
                    ))}
                  </Grid>
                </ColorPicker.SwatchGroup>
              </ColorPicker.Root>
            </Popover.Body>
          </Popover.Content>
        </Popover.Positioner>
      </Portal>
    </Popover.Root>
  );
}

const swatches = [
  'red',
  'pink',
  'purple',
  'cyan',
  'blue',
  'teal',
  'green',
  'yellow',
  'orange',
  'gray',
];
