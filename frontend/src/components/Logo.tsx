import { Box, Text } from '@chakra-ui/react';

const Logo = () => {
  return (
    <Box>
      <Text fontSize='lg' fontWeight='bold' color='blue.600'>
        Logo
      </Text>
      {/* Or use an actual image */}
      {/* <Image src="/logo.png" alt="Logo" height="40px" /> */}
    </Box>
  );
};

export default Logo;
