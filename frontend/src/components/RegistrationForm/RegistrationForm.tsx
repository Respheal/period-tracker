import { useState } from 'react';
import { useForm } from '@tanstack/react-form';

import { type UserCreate } from '@/client/types.gen';
import { Button, Input, Stack } from '@chakra-ui/react';

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
    <form
      onSubmit={(e) => {
        e.preventDefault();
        e.stopPropagation();
        setLoading(true);
        form.handleSubmit();
      }}>
      Register
      <Stack direction='column'>
        <form.Field
          name='username'
          children={(field) => {
            return (
              <Input
                required
                id={field.name}
                name={field.name}
                value={field.state.value}
                onChange={(e) => field.handleChange(e.target.value)}
              />
            );
          }}
        />
        <form.Field
          name='display_name'
          children={(field) => (
            <Input
              id={field.name}
              name={field.name}
              value={field.state.value}
              onChange={(e) => field.handleChange(e.target.value)}
            />
          )}
        />
        <form.Field
          name='password'
          children={(field) => (
            <Input
              required
              type='password'
              id={field.name}
              name={field.name}
              value={field.state.value}
              onChange={(e) => field.handleChange(e.target.value)}
            />
          )}
        />
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
              <Input
                required
                type='password'
                value={field.state.value}
                onChange={(e) => field.handleChange(e.target.value)}
                // error={field.state.meta.errors.length > 0}
                // helperText={field.state.meta.errors.join(', ') || ' '}
              />
            </>
          )}
        </form.Field>
      </Stack>
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
            <Button type='submit' loading={loading} disabled={disabled}>
              Register
            </Button>
          );
        }}
      />
    </form>
  );
}
