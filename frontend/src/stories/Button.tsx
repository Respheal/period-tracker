import { Button as MatButton } from "@mui/material";
import "./button.css";

export interface ButtonProps {
  usage?: "primary" | "secondary" | "error" | "warning" | "info" | "success";
  size?: "small" | "medium" | "large";
  variant?: "text" | "contained" | "outlined";
  disableElevation?: boolean;
  label: string;
  onClick?: () => void;
}

/** Primary UI component for user interaction */
export const Button = ({
  usage = "primary",
  size = "medium",
  variant = "contained",
  label,
  disableElevation = false,
  ...props
}: ButtonProps) => {
  return (
    <>
      <MatButton
        variant={variant}
        size={size}
        color={usage}
        disableElevation={variant == "contained" ? disableElevation : false}
        {...props}
      >
        {label}
      </MatButton>
    </>
  );
};
