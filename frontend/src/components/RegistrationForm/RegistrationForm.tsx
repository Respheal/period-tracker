import { useState } from 'react';
import { useForm } from '@tanstack/react-form';

import { type UserCreate } from '@/client/types.gen';
import { PasswordInput } from '@/components/ui/password-input';
import { Button, Stack, Field, Input, Container, Card, Text } from '@chakra-ui/react';

interface RegistrationForm extends UserCreate {
  confirm_password: string;
}

export function RegistrationForm({
  registerFn,
  navigateFn,
}: {
  registerFn: (data: UserCreate) => void;
  navigateFn: ({ to }: { to: string }) => void;
}) {
  const [loading, setLoading] = useState(false);
  const defaultUser = {
    username: '',
    password: '',
    confirm_password: '',
  } as RegistrationForm;
  const form = useForm({
    defaultValues: defaultUser,
    onSubmit: async ({ value }) => {
      registerFn({
        username: value.username,
        display_name: value.display_name,
        password: value.password,
      });
      setLoading(false);
    },
  });

  return (
    <Container maxW={'lg'}>
      <Card.Root>
        <Card.Header>
          <Card.Title>Register</Card.Title>
        </Card.Header>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setLoading(true);
            void form.handleSubmit();
          }}>
          <Card.Body>
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
                      value={field.state.value ?? ''}
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

              <Field.Root required invalid>
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
                        <Field.ErrorText>
                          <Text key={err}>{err}</Text>
                        </Field.ErrorText>
                      ))}
                    </>
                  )}
                </form.Field>
              </Field.Root>
            </Stack>
          </Card.Body>
          <Card.Footer justifyContent='flex-end'>
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
          </Card.Footer>
        </form>
      </Card.Root>
    </Container>
  );
}
