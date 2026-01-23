import { TanStackDevtools } from "@tanstack/react-devtools";
import { formDevtoolsPlugin } from "@tanstack/react-form-devtools";

import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import SaveIcon from "@mui/icons-material/Save";

import { useForm } from "@tanstack/react-form";
import type { AnyFieldApi } from "@tanstack/react-form";
import dayjs from "dayjs";

interface Period {
  startDate: string;
  endDate: string | null;
}
const defaultValues: Period = {
  startDate: dayjs().format("YYYY-MM-DD"),
  endDate: null,
};

function FieldInfo({ field }: { field: AnyFieldApi }) {
  return (
    <>
      {field.state.meta.isTouched && !field.state.meta.isValid ? (
        <em>{field.state.meta.errors.join(",")}</em>
      ) : null}
      {field.state.meta.isValidating ? "Validating..." : null}
    </>
  );
}

export default function PeriodLogger() {
  const form = useForm({
    defaultValues: defaultValues,
    onSubmit: async ({ value }) => {
      // Do something with form data
      console.log(value);
    },
  });
  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Box
        component="section"
        sx={{ flexGrow: 1, p: 2, border: "1px dashed grey" }}
      >
        <form
          onSubmit={(e) => {
            e.preventDefault();
            e.stopPropagation();
            form.handleSubmit();
          }}
        >
          <Grid container spacing={1}>
            <Grid container size={12}>
              <Typography variant="h6" noWrap component="div">
                Log Period
              </Typography>
            </Grid>
            <Grid
              container
              size={12}
              sx={{ justifyContent: "flex-start", alignItems: "flex-start" }}
            >
              <form.Field
                name="startDate"
                children={(field) => {
                  return (
                    <DatePicker
                      label="Start Date"
                      name={field.name}
                      value={dayjs(field.state.value)}
                      onChange={(date) => {
                        field.handleChange(
                          date ? date.format("YYYY-MM-DD") : "",
                        );
                      }}
                    />
                  );
                }}
              />
              <form.Field
                name="endDate"
                validators={{
                  // endDate must be after startDate
                  onChange: ({ value }) => {
                    const startDate = dayjs(form.getFieldValue("startDate"));
                    const endDate = dayjs(value);
                    if (value && endDate.isBefore(startDate)) {
                      return "End date must be after start date";
                    }
                  },
                }}
                children={(field) => {
                  return (
                    <>
                      <DatePicker
                        label="End Date"
                        name={field.name}
                        slotProps={{
                          field: {
                            clearable: true,
                            onClear: () => field.handleChange(""),
                          },
                          textField: {
                            helperText: <FieldInfo field={field} />,
                          },
                        }}
                        onChange={(date) => {
                          field.handleChange(
                            date ? date.format("YYYY-MM-DD") : "",
                          );
                        }}
                      />
                    </>
                  );
                }}
              />
            </Grid>
            <Grid container size={12} sx={{ justifyContent: "flex-end" }}>
              <form.Subscribe
                selector={(state) => [state.canSubmit, state.isSubmitting]}
                children={([canSubmit, isSubmitting]) => (
                  <Button
                    loading={isSubmitting}
                    disabled={!canSubmit}
                    loadingPosition="start"
                    startIcon={<SaveIcon />}
                    variant="outlined"
                    type="submit"
                    name="submit"
                  >
                    Save
                  </Button>
                )}
              />
            </Grid>
          </Grid>
        </form>
      </Box>
      <TanStackDevtools plugins={[formDevtoolsPlugin()]} />
    </LocalizationProvider>
  );
}
