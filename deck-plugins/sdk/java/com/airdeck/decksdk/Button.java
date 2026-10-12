package com.airdeck.decksdk;

public final class Button {
  public String id;
  public String title;
  public String icon_key;
  public int columns;
  public int rows;
  public String action;
  public String plugin_id;
  /** When true, appears in Button Editor for tap buttons. */
  public boolean editor_tap;
  /** When true, appears in Button Editor for toggle buttons. */
  public boolean editor_toggle;

  public Button(String id, String title, String action, String pluginId) {
    this.id = id;
    this.title = title;
    this.action = action;
    this.plugin_id = pluginId;
    this.columns = 1;
    this.rows = 1;
  }
}
