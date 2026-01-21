import { createFileRoute } from "@tanstack/react-router";
import Button from "@mui/material/Button";

export const Route = createFileRoute("/")({
  component: RouteComponent,
});

function RouteComponent() {
  return (
    <div>
      <Button variant="contained">Hello "/"!</Button>
    </div>
  );
}
