import { useForm } from '@tanstack/react-form';
import { useState } from 'react';
import { Button, Stack, Field, Input, Container, Card } from '@chakra-ui/react';

import { PasswordInput } from '@/components/ui/password-input';
import type { BodyLoginAuthPost } from '@/client/types.gen';

export function LoginForm({
  loginFn,
  navigateFn,
}: {
  loginFn: (data: BodyLoginAuthPost) => void;
  navigateFn: ({ to }: { to: string }) => void;
}) {
  const [submitting, setSubmitting] = useState(false);
  const form = useForm({
    defaultValues: {
      username: '',
      password: '',
    },
    onSubmit: async ({ value }) => {
      const data: BodyLoginAuthPost = {
        username: value.username,
        password: value.password,
      };
      loginFn(data);
      setSubmitting(false);
    },
  });

  return (
    <Container maxW={'lg'}>
      <Card.Root>
        <Card.Header>
          <Card.Title>Login</Card.Title>
        </Card.Header>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setSubmitting(true);
            void form.handleSubmit();
          }}>
          <Card.Body>
            <Stack gap='2' align='flex-start' maxW='sm'>
              <form.Field name='username'>
                {(field) => (
                  <Field.Root required>
                    <Field.Label>
                      Username <Field.RequiredIndicator />
                    </Field.Label>
                    <Input
                      value={field.state.value}
                      onChange={(e) => field.handleChange(e.target.value)}
                    />
                  </Field.Root>
                )}
              </form.Field>

              <form.Field name='password'>
                {(field) => (
                  <Field.Root required>
                    <Field.Label>
                      Password <Field.RequiredIndicator />
                    </Field.Label>
                    <PasswordInput
                      value={field.state.value}
                      onChange={(e) => field.handleChange(e.target.value)}
                    />
                  </Field.Root>
                )}
              </form.Field>
            </Stack>
          </Card.Body>
          <Card.Footer justifyContent='flex-end'>
            <Button onClick={() => navigateFn({ to: '/register' })}>Register</Button>
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
                  <Button type='submit' loading={submitting} disabled={disabled}>
                    Login
                  </Button>
                );
              }}
            />
          </Card.Footer>
        </form>
      </Card.Root>
    </Container>
  );
}
