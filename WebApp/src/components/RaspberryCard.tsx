import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardFooter,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { fetchRaspberryData } from "@/lib/firebase";
import type { RaspberryData } from "@/types";
import { DropletIcon, FlameIcon, RefreshCwIcon } from "lucide-react";
import { useTheme } from "./theme-provider";

export function RaspberryCard() {
  const [raspberryData, setRaspberryData] = useState<RaspberryData | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { theme } = useTheme();
  const isDarkMode =
    theme === "dark" ||
    (theme === "system" &&
      window.matchMedia("(prefers-color-scheme: dark)").matches);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchRaspberryData();
      setRaspberryData(data);
    } catch (err) {
      setError("Erreur lors de la récupération des données");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Charger les données au premier rendu
  useEffect(() => {
    loadData();
  }, []);

  // Formater une date depuis un timestamp
  const formatDate = (timestamp: number) => {
    return new Date(timestamp).toLocaleString("fr-FR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  return (
    <Card
      className={`w-full max-w-md mx-auto shadow-lg hover:shadow-xl transition-shadow ${
        isDarkMode ? "bg-zinc-900 border-zinc-800" : "bg-white"
      }`}
    >
      <CardHeader
        className={`${
          isDarkMode
            ? "bg-gradient-to-r from-blue-950 via-indigo-800 to-blue-950"
            : "bg-gradient-to-r from-blue-100 via-indigo-100 to-blue-200"
        }`}
      >
        <CardTitle
          className={`text-xl font-bold ${
            isDarkMode ? "text-white" : "text-zinc-900"
          }`}
        >
          Capteurs Raspberry Pi
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-6">
        {error ? (
          <div className="text-red-500 text-center py-4">{error}</div>
        ) : loading ? (
          <div
            className={`text-center py-4 ${
              isDarkMode ? "text-zinc-300" : "text-zinc-800"
            }`}
          >
            Chargement...
          </div>
        ) : raspberryData ? (
          <div className="space-y-4">
            <div
              className={`flex items-center justify-between p-3 rounded-lg ${
                isDarkMode ? "bg-blue-900" : "bg-blue-50"
              }`}
            >
              <div className="flex items-center">
                <DropletIcon
                  className={`mr-2 ${
                    isDarkMode ? "text-blue-400" : "text-blue-500"
                  }`}
                  size={24}
                />
                <span
                  className={`font-medium ${
                    isDarkMode ? "text-zinc-50" : "text-zinc-900"
                  }`}
                >
                  Humidité
                </span>
              </div>
              <div
                className={`text-lg font-bold ${
                  isDarkMode ? "text-zinc-50" : "text-zinc-900"
                }`}
              >
                {raspberryData.humidity.value}%
              </div>
            </div>

            {raspberryData.gas && (
              <div
                className={`flex items-center justify-between p-3 rounded-lg ${
                  isDarkMode ? "bg-orange-900" : "bg-orange-50"
                }`}
              >
                <div className="flex items-center">
                  <FlameIcon
                    className={`mr-2 ${
                      isDarkMode ? "text-orange-400" : "text-orange-500"
                    }`}
                    size={24}
                  />
                  <span
                    className={`font-medium ${
                      isDarkMode ? "text-zinc-50" : "text-zinc-900"
                    }`}
                  >
                    Gaz
                  </span>
                </div>
                <div
                  className={`text-lg font-bold ${
                    isDarkMode ? "text-zinc-50" : "text-zinc-900"
                  }`}
                >
                  {raspberryData.gas.value} ppm
                </div>
              </div>
            )}

            <div
              className={`text-xs text-right mt-2 ${
                isDarkMode ? "text-gray-400" : "text-gray-600"
              }`}
            >
              Dernière mise à jour:{" "}
              {formatDate(raspberryData.humidity.last_updated)}
            </div>
          </div>
        ) : (
          <div
            className={`text-center py-4 ${
              isDarkMode ? "text-zinc-300" : "text-zinc-800"
            }`}
          >
            Aucune donnée disponible
          </div>
        )}
      </CardContent>
      <CardFooter
        className={`flex justify-center border-t pt-4 ${
          isDarkMode ? "border-zinc-800" : ""
        }`}
      >
        <Button onClick={loadData} disabled={loading} className="w-full">
          <RefreshCwIcon
            className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`}
          />
          Rafraîchir
        </Button>
      </CardFooter>
    </Card>
  );
}
