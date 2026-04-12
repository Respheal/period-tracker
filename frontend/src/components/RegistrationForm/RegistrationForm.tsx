import { useState } from 'react';
import { useForm } from '@tanstack/react-form';

import { type UserCreate } from '@/client/types.gen';
import { PasswordInput } from '@/components/ui/password-input';
import { Button, Stack, Field, Input, Container, Card, Text } from '@chakra-ui/react';

export function RegistrationForm({
  registerFn,
  navigateFn,
}: {
  registerFn: (data: UserCreate) => void;
  navigateFn: ({ to }: { to: string }) => void;
}) {
  const [loading, setLoading] = useState(false);
  const form = useForm({
    defaultValues: {
      username: '',
      password: '',
      confirm_password: '',
      display_name: '',
    },
    onSubmit: async ({ value }) => {
      console.log('Submitting form with value:', value);
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
    <Container maxW={'lg'}>
      <Card.Root>
        <Card.Header>
          <Card.Title>Register</Card.Title>
        </Card.Header>
        <Card.Body>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              e.stopPropagation();
              void form.handleSubmit();
            }}>
            <Stack gap='2' align='flex-start' maxW='sm'>
              <Field.Root required>
                <Field.Label>
                  Username <Field.RequiredIndicator />
                </Field.Label>
                <form.Field name='username'>
                  {(field) => (
                    <Input
                      value={field.state.value}
                      onChange={(e) => field.handleChange(e.target.value)}
                    />
                  )}
                </form.Field>
              </Field.Root>

              <Field.Root>
                <Field.Label>Display Name</Field.Label>
                <form.Field name='display_name'>
                  {(field) => (
                    <Input
                      value={field.state.value}
                      onChange={(e) => field.handleChange(e.target.value)}
                    />
                  )}
                </form.Field>
              </Field.Root>

              <Field.Root required>
                <Field.Label>
                  Password <Field.RequiredIndicator />
                </Field.Label>
                <form.Field name='password'>
                  {(field) => (
                    <PasswordInput
                      value={field.state.value}
                      onChange={(e) => field.handleChange(e.target.value)}
                    />
                  )}
                </form.Field>
              </Field.Root>

              <Field.Root required>
                <Field.Label>
                  Confirm Password <Field.RequiredIndicator />
                </Field.Label>
                <form.Field
                  name='confirm_password'
                  validators={{
                    onChangeListenTo: ['password'],
                    onChange: ({ value, fieldApi }) => {
                      if (
                        form.getFieldMeta('confirm_password')?.isTouched &&
                        value !== fieldApi.form.getFieldValue('password')
                      ) {
                        return 'Passwords do not match';
                      }
                      return undefined;
                    },
                  }}>
                  {(field) => (
                    <>
                      <PasswordInput
                        value={field.state.value}
                        onChange={(e) => field.handleChange(e.target.value)}
                      />
                      {field.state.meta.errors.map((err) => (
                        <Text key={err}>{err}</Text>
                      ))}
                    </>
                  )}
                </form.Field>
              </Field.Root>

              <Stack direction='row' gap='2'>
                <Button onClick={() => navigateFn({ to: '/login' })}>Login</Button>
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
                      <Button type='submit' loading={loading} disabled={disabled}>
                        Register
                      </Button>
                    );
                  }}
                />
              </Stack>
            </Stack>
          </form>
        </Card.Body>
        <Card.Footer />
      </Card.Root>
    </Container>
  );
}
