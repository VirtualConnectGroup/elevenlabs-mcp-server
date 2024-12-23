import { error } from "@sveltejs/kit";
import type { RequestHandler } from "./$types";

export const GET: RequestHandler = async ({ url }) => {
  const fileId = url.searchParams.get("id");
  if (!fileId) {
    throw error(400, "Missing file ID");
  }

  try {
    const response = await fetch(`/api/history/download?id=${fileId}`);
    if (!response.ok) {
      throw error(404, "File not found");
    }

    const audioBlob = await response.blob();
    return new Response(audioBlob, {
      headers: {
        "Content-Type": "audio/mpeg",
        "Content-Disposition": `attachment; filename="voiceover-${fileId}.mp3"`,
      },
    });
  } catch (e) {
    console.error("Download error:", e);
    throw error(500, "Failed to download file");
  }
};
