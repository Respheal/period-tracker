// Hook to manage cookies (specifically the refresh_token cookie)

const useCookie = () => {
  const setCookie = (
    name: string,
    value: string,
    exdays?: number | null,
    secure: boolean = true,
  ) => {
    const d = new Date();
    if (!exdays) {
      exdays = import.meta.env.REFRESH_TOKEN_EXPIRE_DAYS
        ? parseInt(import.meta.env.REFRESH_TOKEN_EXPIRE_DAYS)
        : 7;
    }
    d.setTime(d.getTime() + exdays * 24 * 60 * 60 * 1000);
    const expires = `expires=${d.toUTCString()}`;
    const secureFlag = secure ? "Secure; " : "";
    const cookie = `${name}=${value}; ${expires}; ${secureFlag}SameSite=Strict; path=/`;
    document.cookie = cookie;
  };

  const getCookie = (name: string) => {
    const cname = `${name}=`;
    const decodedCookie = decodeURIComponent(document.cookie);
    const ca = decodedCookie.split(";");
    for (let i = 0; i < ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) == " ") {
        c = c.substring(1);
      }
      if (c.indexOf(cname) == 0) {
        return c.substring(cname.length, c.length);
      }
    }
    return "";
  };

  const expireCookie = (name: string) => {
    setCookie(name, "", -1, true);
  };

  return {
    setCookie,
    getCookie,
    expireCookie,
  };
};

export default useCookie;
