import { createFileRoute } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';

import { readMeUsersMeGetOptions } from '@/client/@tanstack/react-query.gen';

export const Route = createFileRoute('/_authenticated/api')({
  component: RouteComponent,
});

function RouteComponent() {
  // const { data, isLoading, error } = useQuery({ ...healthCheckHealthGetOptions() });
  const { data, isLoading, error } = useQuery({ ...readMeUsersMeGetOptions() });

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error instanceof Error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <>
      <p>It me: {data?.username}</p>
      {/* <p>Status: {result.data?.status}</p>
      <p>Timestamp: {result.data?.timestamp?.toISOString()}</p> */}
    </>
  );
}
