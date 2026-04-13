import { useState, useEffect, useMemo } from 'react';
import { useForm, useStore } from '@tanstack/react-form';
import { zxcvbn, zxcvbnOptions } from '@zxcvbn-ts/core';
import { Button, Stack, Field, Input, Card, Text } from '@chakra-ui/react';

import { type UserCreate } from '@/client/types.gen';
import { PasswordInput, PasswordStrengthMeter } from '@/components/ui/password-input';

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
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadZxcvbn = async () => {
      const common = await import('@zxcvbn-ts/language-common');
      const en = await import('@zxcvbn-ts/language-en');

      zxcvbnOptions.setOptions({
        useLevenshteinDistance: true,
        dictionary: { ...common.dictionary, ...en.dictionary },
        graphs: common.adjacencyGraphs,
        translations: en.translations,
      });
      setLoading(false);
    };
    loadZxcvbn();
  }, []);

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
      setSubmitting(false);
    },
  });

  const passwordValue = useStore(form.store, (state) => state.values.password);
  const strengthResult = useMemo(() => {
    if (passwordValue && !loading) {
      return zxcvbn(passwordValue);
    }
    return null;
  }, [passwordValue, loading]);

  const score = strengthResult?.score ?? 0;

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

            <form.Field name='password'>
              {(field) => (
                <Field.Root required>
                  <Field.Label>
                    Password <Field.RequiredIndicator />
                  </Field.Label>
                  <Stack width={'full'}>
                    <PasswordInput
                      value={field.state.value}
                      onChange={(e) => field.handleChange(e.target.value)}
                    />
                    <PasswordStrengthMeter value={score} />
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
    </Card.Root>
  );
}
