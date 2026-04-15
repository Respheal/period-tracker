import { Link } from '@tanstack/react-router';
import { HStack, VStack, Link as ChakraLink } from '@chakra-ui/react';

export function MenuLinks({
  nav_items = [],
  isMobile = false,
  logoutFn,
}: {
  nav_items: readonly (readonly [string, string])[];
  isMobile?: boolean;
  logoutFn: () => void;
}) {
  const LinkComponent = isMobile ? VStack : HStack;

  return (
    <LinkComponent gap={isMobile ? 4 : 8}>
      {nav_items.map(([href, name]) => (
        <ChakraLink asChild key={name}>
          <Link to={href} activeProps={{ style: { fontWeight: 'bold' } }}>
            {name}
          </Link>
        </ChakraLink>
      ))}
      <ChakraLink onClick={logoutFn}>Log Out</ChakraLink>
    </LinkComponent>
  );
}
