import { usePasswordStrength } from '@/hooks/useZxcvbn';
import { Button, Card, Field, Input, Stack, Text } from '@chakra-ui/react';
import { useForm, useSelector } from '@tanstack/react-form';
import type { ToOptions } from '@tanstack/react-router';
import { useState } from 'react';

import { type UserCreate } from '@/client/types.gen';
import {
  PasswordInput,
  PasswordStrengthMeter,
} from '@/components/chakra-ui/password-input';
import { toaster, Toaster } from '@/components/chakra-ui/toaster';

interface RegistrationFormProps {
  navigateFn: (options: ToOptions) => Promise<void>;
  registerFn: (data: UserCreate) => Promise<void>;
}

interface RegistrationForm extends UserCreate {
  confirm_password: string;
}

export function RegistrationForm({ registerFn, navigateFn }: RegistrationFormProps) {
  const [submitting, setSubmitting] = useState(false);

  const defaultUser = {
    username: '',
    password: '',
    confirm_password: '',
  } as RegistrationForm;

  const form = useForm({
    defaultValues: defaultUser,
    onSubmit: async ({ value }) => {
      await registerFn({
        username: value.username,
        display_name: value.display_name,
        password: value.password,
      }).catch((err: Error) => {
        toaster.create({
          title: err.message || 'Registration failed',
          type: 'error',
        });
      });
      setSubmitting(false);
      void navigateFn({ to: '/login' });
    },
  });

  const passwordValue = useSelector(form.store, (state) => state.values.password);
  const { result: strengthResult } = usePasswordStrength(passwordValue);
  const pwned = strengthResult?.feedback?.warning?.includes('data breach') || false;

  return (
    <Card.Root minW={'sm'}>
      <Card.Header>
        <Card.Title>Register</Card.Title>
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

            <form.Field name='display_name'>
              {(field) => (
                <Field.Root>
                  <Field.Label>Display Name</Field.Label>
                  <Input
                    value={field.state.value ?? ''}
                    onChange={(e) => field.handleChange(e.target.value)}
                  />
                </Field.Root>
              )}
            </form.Field>

            <form.Field
              name='password'
              validators={{
                onChange: () => {
                  if (strengthResult?.feedback?.warning) {
                    return strengthResult.feedback.warning;
                  }
                  return undefined;
                },
              }}>
              {(field) => (
                <Field.Root required invalid={!!strengthResult?.feedback?.warning}>
                  <Field.Label>
                    Password <Field.RequiredIndicator />
                  </Field.Label>
                  <Stack width={'full'}>
                    <PasswordInput
                      value={field.state.value}
                      onChange={(e) => field.handleChange(e.target.value)}
                    />
                    <Field.ErrorText>
                      {strengthResult?.feedback?.warning}{' '}
                      {pwned && (
                        <a
                          href='https://haveibeenpwned.com/Passwords'
                          target='_blank'
                          rel='noopener noreferrer'>
                          Check here.
                        </a>
                      )}
                    </Field.ErrorText>
                    <PasswordStrengthMeter value={strengthResult?.score ?? 0} />
                  </Stack>
                </Field.Root>
              )}
            </form.Field>

            <form.Field
              name='confirm_password'
              validators={{
                onChangeListenTo: ['password'],
                onChange: ({ value, fieldApi }) => {
                  const isDirty =
                    fieldApi.state.meta.isTouched || fieldApi.state.meta.isDirty;
                  if (isDirty && value !== fieldApi.form.getFieldValue('password')) {
                    return 'Passwords do not match';
                  }
                  return undefined;
                },
              }}>
              {(field) => (
                <Field.Root required invalid={field.state.meta.errors.length > 0}>
                  <Field.Label>
                    Confirm Password <Field.RequiredIndicator />
                  </Field.Label>
                  <PasswordInput
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                  />
                  {field.state.meta.errors.map((err, index) => {
                    return (
                      // eslint-disable-next-line react-x/no-array-index-key
                      <Field.ErrorText key={index}>
                        <Text>{err}</Text>
                      </Field.ErrorText>
                    );
                  })}
                </Field.Root>
              )}
            </form.Field>
          </Stack>
        </Card.Body>
        <Card.Footer justifyContent='flex-end'>
          <Button onClick={() => void navigateFn({ to: '/login' })}>Login</Button>
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
              const disabled = !state.canSubmit || state.isSubmitting || !allFieldsFilled;
              return (
                <Button type='submit' loading={submitting} disabled={disabled}>
                  Register
                </Button>
              );
            }}
          />
        </Card.Footer>
      </form>
      <Toaster />
    </Card.Root>
  );
}
