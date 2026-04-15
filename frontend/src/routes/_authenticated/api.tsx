import { createFileRoute } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';

import { healthCheckHealthGetOptions } from '@/client/@tanstack/react-query.gen';

export const Route = createFileRoute('/_authenticated/api')({
  component: RouteComponent,
});

function RouteComponent() {
  const { data, isLoading, error } = useQuery({ ...healthCheckHealthGetOptions() });

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <>
      <p>Status: {data?.status}</p>
      <p>Timestamp: {data?.timestamp?.toISOString()}</p>
    </>
  );
}
