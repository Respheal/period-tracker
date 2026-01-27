import type { BodyLoginAuthPost } from "@/client/types.gen";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardActions from "@mui/material/CardActions";
import CardContent from "@mui/material/CardContent";
import Container from "@mui/material/Container";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useForm } from "@tanstack/react-form";
import { useState } from "react";

export default function Login({
  loginFn,
  navigateFn,
}: {
  loginFn: (data: BodyLoginAuthPost) => void;
  navigateFn: ({ to }: { to: string }) => void;
}) {
  const [loading, setLoading] = useState(false);
  const form = useForm({
    defaultValues: {
      username: "",
      password: "",
    },
    onSubmit: async ({ value }) => {
      const data: BodyLoginAuthPost = {
        username: value.username,
        password: value.password,
      };
      loginFn(data);
      setLoading(false);
    },
  });

  return (
    <Container maxWidth="xs">
      <Box
        display="flex"
        alignItems="center"
        justifyContent="center"
        height="100vh"
        sx={{ minWidth: 275 }}
      >
        <Card variant="outlined">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              e.stopPropagation();
              setLoading(true);
              form.handleSubmit();
            }}
          >
            <CardContent sx={{ paddingBottom: 0 }}>
              <Stack direction="column" spacing={1}>
                <Typography variant="h5" component="div" gutterBottom>
                  Login
                </Typography>
                <form.Field
                  name="username"
                  children={(field) => {
                    return (
                      <TextField
                        required
                        label="Username"
                        id={field.name}
                        name={field.name}
                        value={field.state.value}
                        onChange={(e) => field.handleChange(e.target.value)}
                      />
                    );
                  }}
                />
                <form.Field
                  name="password"
                  children={(field) => (
                    <TextField
                      required
                      label="Password"
                      id={field.name}
                      name={field.name}
                      value={field.state.value}
                      onChange={(e) => field.handleChange(e.target.value)}
                    />
                  )}
                />
              </Stack>
            </CardContent>
            <CardActions sx={{ paddingBottom: 2, justifyContent: "flex-end" }}>
              <form.Subscribe
                selector={(state) => ({
                  canSubmit: state.canSubmit,
                  isSubmitting: state.isSubmitting,
                  username: state.values.username,
                  password: state.values.password,
                })}
                children={(state) => {
                  const allFieldsFilled = state.username && state.password;
                  const disabled =
                    !state.canSubmit || state.isSubmitting || !allFieldsFilled;
                  return (
                    <>
                      <Button onClick={() => navigateFn({ to: "/register" })}>
                        Register
                      </Button>
                      <Button
                        variant="contained"
                        type="submit"
                        loading={loading}
                        disabled={disabled}
                      >
                        Login
                      </Button>
                    </>
                  );
                }}
              />
            </CardActions>
          </form>
        </Card>
      </Box>
    </Container>
  );
}
