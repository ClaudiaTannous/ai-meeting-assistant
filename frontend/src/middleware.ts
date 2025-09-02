import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Define routes that need authentication
const protectedRoutes = ["/meetings"];

export function middleware(req: NextRequest) {
  const token = req.cookies.get("token")?.value || null;

  // If user tries to access protected route without token
  if (protectedRoutes.some((route) => req.nextUrl.pathname.startsWith(route))) {
    if (!token) {
      const loginUrl = new URL("/login", req.url);
      return NextResponse.redirect(loginUrl);
    }
  }

  return NextResponse.next();
}

// Match all routes, but you can exclude static files
export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
