import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { healthCheckHealthGetOptions } from "../client/@tanstack/react-query.gen";

export const Route = createFileRoute("/api")({
  component: RouteComponent,
});

function RouteComponent() {
  //const { data, isLoading, error } = useQuery(healthCheckHealthGetOptions())
  const { data, isLoading, error } = useQuery({
    ...healthCheckHealthGetOptions(),
    staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
    gcTime: 10 * 60 * 1000, // Keep unused data in cache for 10 minutes
    refetchOnWindowFocus: false, // Don't refetch when window regains focus
  });

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
