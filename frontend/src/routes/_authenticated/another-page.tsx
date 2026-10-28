import { Link as ChakraLink } from '@chakra-ui/react';
import { createFileRoute, Link } from '@tanstack/react-router';

export const Route = createFileRoute('/_authenticated/another-page')({
  component: RouteComponent,
});

function RouteComponent() {
  return (
    <div>
      Hello "/_authenticated/another-page"!{' '}
      <ChakraLink asChild key='home'>
        <Link to='/' activeProps={{ style: { fontWeight: 'bold' } }}>
          Home
        </Link>
      </ChakraLink>
    </div>
  );
}
