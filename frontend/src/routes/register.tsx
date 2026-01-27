// import useAuth from "@/hooks/useAuth";
// import Register from "@/stories/pages/Register/Register";
import {
  createFileRoute,
  //useNavigate
} from "@tanstack/react-router";

export const Route = createFileRoute("/register")({
  component: RouteComponent,
});

function RouteComponent() {
  //const navigate = useNavigate();
  //const {createAccount} = useAuth();

  //return <Register navigateFn={navigate} registerFn={} />;
  return <div>Register Page</div>;
}
