import { useState } from "react";
import { useForm } from "@tanstack/react-form";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardActions from "@mui/material/CardActions";
import CardContent from "@mui/material/CardContent";
import Container from "@mui/material/Container";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";

import type { UserCreate } from "@/client/types.gen";
import Typography from "@mui/material/Typography";

export default function Register({
  registerFn,
  navigateFn,
}: {
  registerFn: (data: UserCreate) => void;
  navigateFn: ({ to }: { to: string }) => void;
}) {
  const [loading, setLoading] = useState(false);
  const form = useForm({
    defaultValues: {
      username: "",
      password: "",
      confirm_password: "",
      display_name: "",
    },
    onSubmit: async ({ value }) => {
      const data: UserCreate = {
        username: value.username,
        display_name: value.display_name,
        password: value.password,
      };
      registerFn(data);
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
              <Typography variant="h5" component="div" gutterBottom>
                Register
              </Typography>
              <Stack direction="column" spacing={1}>
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
                  name="display_name"
                  children={(field) => (
                    <TextField
                      label="Display Name"
                      id={field.name}
                      name={field.name}
                      value={field.state.value}
                      onChange={(e) => field.handleChange(e.target.value)}
                    />
                  )}
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
                <form.Field
                  name="confirm_password"
                  validators={{
                    onChangeListenTo: ["password"],
                    onChange: ({ value, fieldApi }) => {
                      if (
                        form.getFieldMeta("confirm_password")?.isTouched &&
                        value !== fieldApi.form.getFieldValue("password")
                      ) {
                        return "Passwords do not match";
                      }
                      return undefined;
                    },
                  }}
                >
                  {(field) => (
                    <>
                      <TextField
                        required
                        label="Confirm Password"
                        value={field.state.value}
                        onChange={(e) => field.handleChange(e.target.value)}
                        error={field.state.meta.errors.length > 0}
                        helperText={field.state.meta.errors.join(", ") || " "}
                      />
                    </>
                  )}
                </form.Field>
              </Stack>
            </CardContent>
            <CardActions sx={{ paddingBottom: 2, justifyContent: "flex-end" }}>
              <Button onClick={() => navigateFn({ to: "/login" })}>
                Login
              </Button>
              <form.Subscribe
                selector={(state) => ({
                  canSubmit: state.canSubmit,
                  isSubmitting: state.isSubmitting,
                  username: state.values.username,
                  password: state.values.password,
                  confirm_password: state.values.confirm_password,
                })}
                children={(state) => {
                  const allFieldsFilled =
                    state.username && state.password && state.confirm_password;
                  const disabled =
                    !state.canSubmit || state.isSubmitting || !allFieldsFilled;
                  return (
                    <Button
                      variant="contained"
                      type="submit"
                      loading={loading}
                      disabled={disabled}
                    >
                      Register
                    </Button>
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
