import { useState } from 'react';
import { useForm } from '@tanstack/react-form';
import { type ToOptions } from '@tanstack/react-router';
import { Button, Stack, Field, Input, Card } from '@chakra-ui/react';

import { PasswordInput } from '@/components/chakra-ui/password-input';
import type { BodyLoginAuthPost } from '@/client/types.gen';

interface LoginFormProps {
  navigateFn: (options: ToOptions) => Promise<void>;
  loginFn: (data: BodyLoginAuthPost) => Promise<void>;
}

export function LoginForm({ loginFn, navigateFn }: LoginFormProps) {
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
      await loginFn(data);
      setSubmitting(false);
    },
  });

  return (
    <Card.Root minW={'sm'}>
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
          <Stack gap={2}>
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
          <Button onClick={() => void navigateFn({ to: '/register' })}>Register</Button>
          <form.Subscribe
            selector={(state) => ({
              canSubmit: state.canSubmit,
              isSubmitting: state.isSubmitting,
              username: state.values.username,
              password: state.values.password,
            })}
            children={(state) => {
              const allFieldsFilled = state.username && state.password;
              const disabled = !state.canSubmit || state.isSubmitting || !allFieldsFilled;
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
  );
}
