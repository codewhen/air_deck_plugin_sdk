package com.airdeck.decksdk;

import java.util.List;

/**
 * Required contract for Air Mouse .deckPlugin sidecars (Java).
 * Implement {@link DeckPlugin} or the binary is not a valid plugin.
 */
public interface DeckPlugin {
  List<Button> catalog();

  default void poll() throws Exception {}

  void invoke(String type, String action, String bodyJson, String payloadJson) throws Exception;
}
