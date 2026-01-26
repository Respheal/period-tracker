import { createFileRoute } from "@tanstack/react-router";
import useAuth from "@hooks/useAuth";
import { useForm } from "@tanstack/react-form";
import type { BodyLoginAuthPost } from "@/client/types.gen";

export const Route = createFileRoute("/login")({
  component: RouteComponent,
});

function RouteComponent() {
  const { login } = useAuth();
  const form = useForm({
    defaultValues: {
      username: "",
      password: "",
    },
    onSubmit: async ({ value }) => {
      console.log(value);
      const data: BodyLoginAuthPost = {
        username: value.username,
        password: value.password,
      };
      login(data);
    },
  });

  return (
    <div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          e.stopPropagation();
          form.handleSubmit();
        }}
      >
        <div>
          <form.Field
            name="username"
            children={(field) => {
              return (
                <>
                  <label htmlFor={field.name}>Username:</label>
                  <input
                    id={field.name}
                    name={field.name}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                  />
                </>
              );
            }}
          />
        </div>
        <div>
          <form.Field
            name="password"
            children={(field) => (
              <>
                <label htmlFor={field.name}>Password:</label>
                <input
                  id={field.name}
                  name={field.name}
                  value={field.state.value}
                  onChange={(e) => field.handleChange(e.target.value)}
                />
              </>
            )}
          />
        </div>
        <form.Subscribe
          selector={(state) => [state.canSubmit, state.isSubmitting]}
          children={([canSubmit, isSubmitting]) => (
            <>
              <button type="submit" disabled={!canSubmit}>
                {isSubmitting ? "..." : "Login"}
              </button>
            </>
          )}
        />
      </form>
    </div>
  );
}
