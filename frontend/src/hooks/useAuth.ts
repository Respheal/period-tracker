import { useMutation } from "@tanstack/react-query";
import {
  createUserUsersPostMutation,
  loginAuthPostMutation,
  refreshTokensAuthRefreshPostMutation,
} from "../client/@tanstack/react-query.gen";
import { useNavigate } from "@tanstack/react-router";
import { useCookies } from "react-cookie";
import type { BodyLoginAuthPost } from "@/client/types.gen";

const isLoggedIn = () => {
  return localStorage.getItem("access_token") !== null;
};

const useAuth = () => {
  const [cookies, setCookie, removeCookie] = useCookies(["refresh_token"]);
  const navigate = useNavigate();

  const CreateUserMutation = useMutation({
    ...createUserUsersPostMutation(),
    onError: (error) => {
      console.log(error);
    },
    onSuccess: (data) => {
      console.log(data);
      navigate({ to: "/login" });
    },
  });

  const LoginMutation = useMutation({
    ...loginAuthPostMutation(),
    onError: (error) => {
      console.log(error);
    },
    onSuccess: (data) => {
      localStorage.setItem("access_token", data.access_token);
      setCookie("refresh_token", data.refresh_token, {
        path: "/",
        maxAge: 3600,
        secure: true,
        sameSite: "lax",
      });
      navigate({ to: "/" });
    },
  });

  const RefreshMutation = useMutation({
    ...refreshTokensAuthRefreshPostMutation(),
    onError: (error) => {
      console.log(error);
    },
    onSuccess: (data) => {
      localStorage.setItem("access_token", data.access_token);
      setCookie("refresh_token", data.refresh_token, {
        path: "/",
        maxAge: 3600,
        secure: true,
        httpOnly: true,
        sameSite: "lax",
      });
    },
  });

  const createAccount = async (
    username: string,
    password: string,
    display_name?: string | null,
  ) => {
    CreateUserMutation.mutate({
      body: {
        username,
        password,
        display_name,
      },
    });
  };

  const login = async (data: BodyLoginAuthPost) => {
    console.log(data);
    if (LoginMutation.isPending) return;
    LoginMutation.mutate({ body: data });
  };

  const refresh = async () => {
    RefreshMutation.mutate({
      body: {
        refresh_token: cookies["refresh_token"],
      },
    });
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    removeCookie("refresh_token", { path: "/" });
    navigate({ to: "/login" });
  };

  return {
    LoginMutation,
    isLoggedIn,
    createAccount,
    login,
    refresh,
    logout,
  };
};

export { isLoggedIn };
export default useAuth;
